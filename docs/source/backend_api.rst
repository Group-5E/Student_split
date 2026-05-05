Backend API
===========

This page documents the backend API for **Student Split**.
The backend is built using Flask and exposes JSON-based endpoints for authentication, households, expenses, and payments.

Authentication Model
--------------------

The backend uses **Flask-Login** for session-based authentication.

- When a user logs in or registers, Flask-Login creates a **secure session cookie**.
- Clients retain this cookie to remain authenticated.
- Protected endpoints return ``401`` if the cookie is missing or invalid.

Authentication Endpoints
------------------------

These endpoints are registered under the ``auth_bp`` blueprint at ``/api/auth``.

POST /api/auth/register
~~~~~~~~~~~~~~~~~~~~~~~

Creates a new user account and logs them in.

**Request body:**

.. code-block:: json

   {
     "username": "jsmith",
     "name": "John Smith",
     "email": "john@example.com",
     "password": "secret"
   }

**Response:**

.. code-block:: json

   { "success": true }

**Errors:** ``400`` if email is already in use.

POST /api/auth/login
~~~~~~~~~~~~~~~~~~~~

Logs in an existing user.

**Request body:**

.. code-block:: json

   {
     "email": "john@example.com",
     "password": "secret"
   }

**Response:**

.. code-block:: json

   { "success": true }

**Errors:** ``401`` if user not found or password is wrong.

POST /api/auth/logout
~~~~~~~~~~~~~~~~~~~~~

Logs out the current user. Requires authentication.

**Response:**

.. code-block:: json

   { "success": true }

GET /api/auth/me
~~~~~~~~~~~~~~~~

Returns the currently logged-in user's details.

**Response:**

.. code-block:: json

   {
     "user": {
       "id": 1,
       "email": "john@example.com",
       "username": "jsmith"
     }
   }

Returns ``{ "user": null }`` if not logged in.

PUT /api/auth/update
~~~~~~~~~~~~~~~~~~~~

Updates the current user's profile. Requires authentication.

**Request body** (all fields optional):

.. code-block:: json

   {
     "username": "jsmith2",
     "name": "John Smith",
     "email": "new@example.com",
     "allow_multiple_households": true
   }

**Response:** Updated user object.

DELETE /api/auth/delete
~~~~~~~~~~~~~~~~~~~~~~~

Deactivates the current user's account (soft delete). Requires authentication.

**Response:**

.. code-block:: json

   { "success": true }

Household Endpoints
-------------------

These endpoints are registered under the ``households_bp`` blueprint at ``/api/households``.
All endpoints require authentication. Members can only access households they belong to.
Admin-only endpoints are noted below.

GET /api/households/list
~~~~~~~~~~~~~~~~~~~~~~~~

Returns all active households the current user is a member of.

**Response:**

.. code-block:: json

   [
     {
       "id": 1,
       "name": "Flat 3",
       "address": "12 Example Street",
       "created_at": "2026-05-01T10:00:00",
       "role": "admin",
       "member_count": 3
     }
   ]

POST /api/households/create
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creates a new household. The creator is automatically added as an admin member.

**Request body:**

.. code-block:: json

   {
     "name": "Flat 3",
     "address": "12 Example Street"
   }

**Response:** The created household object. ``201`` on success.

GET /api/households/get/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a household's details including its active member list.

**Response:**

.. code-block:: json

   {
     "id": 1,
     "name": "Flat 3",
     "address": "12 Example Street",
     "created_by": 1,
     "created_at": "2026-05-01T10:00:00",
     "members": [
       {
         "user_id": 1,
         "username": "jsmith",
         "name": "John Smith",
         "role": "admin",
         "joined_at": "2026-05-01T10:00:00"
       }
     ]
   }

**Errors:** ``404`` if the household doesn't exist or the user is not a member.

PUT /api/households/update/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updates a household's name or address. **Admin only.**

**Request body** (all fields optional):

.. code-block:: json

   {
     "name": "Flat 3B",
     "address": "14 Example Street"
   }

**Errors:** ``403`` if the user is not an admin.

DELETE /api/households/delete/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Soft-deletes a household (sets ``is_active = false``). **Admin only.**

**Response:**

.. code-block:: json

   { "success": true }

GET /api/households/<id>/members/list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all active members of a household.

POST /api/households/<id>/members/add
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adds a user to the household. **Admin only.**
Accepts ``user_id``, ``username``, or ``email`` to identify the user.

**Request body:**

.. code-block:: json

   { "email": "jane@example.com", "role": "member" }

**Errors:** ``404`` if user not found, ``409`` if already a member.

DELETE /api/households/<id>/members/remove/<user_id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removes a member from the household. Admins can remove anyone; members can only remove themselves.

Expense Endpoints
-----------------

These endpoints are registered under the ``expenses_bp`` blueprint at ``/api/expenses``.
All endpoints require authentication.

GET /api/expenses/list
~~~~~~~~~~~~~~~~~~~~~~

Returns all expenses for a household, newest first.

**Query param:** ``?household_id=1``

**Response:** Array of expense objects, each including their splits.

POST /api/expenses/create
~~~~~~~~~~~~~~~~~~~~~~~~~~

Creates an expense and its splits. The current user is recorded as the payer.

**Request body:**

.. code-block:: json

   {
     "household_id": 1,
     "description": "Weekly shop",
     "amount": 60.00,
     "split_type": "equal",
     "category": "groceries",
     "expense_date": "2026-05-01T12:00:00",
     "splits": [
       { "user_id": 1 },
       { "user_id": 2 },
       { "user_id": 3 }
     ]
   }

**Split types:**

- ``equal`` — amount divided equally, each entry needs only ``user_id``
- ``percentage`` — each entry needs ``user_id`` and ``percentage``
- ``fixed`` — each entry needs ``user_id`` and ``amount_owed``

**Response:** The created expense object. ``201`` on success.

GET /api/expenses/get/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a single expense including all its splits.

PUT /api/expenses/update/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updates an expense. Only the original payer or an admin can edit.
Pass a ``splits`` array to recalculate splits.

DELETE /api/expenses/delete/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Soft-deletes an expense (sets ``is_deleted = true``). Only the payer or admin can delete.
The record is kept for debt tracking purposes.

POST /api/expenses/splits/settle/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Marks an individual split as settled. Only the user who owes the split, or an admin, can settle it.

**Response:**

.. code-block:: json

   { "success": true, "settled_at": "2026-05-01T15:00:00" }

Payment Endpoints
-----------------

These endpoints are registered under the ``payments_bp`` blueprint at ``/api/payments``.
All endpoints require authentication.

GET /api/payments/list
~~~~~~~~~~~~~~~~~~~~~~

Returns all payments for a household, newest first.

**Query param:** ``?household_id=1``

POST /api/payments/create
~~~~~~~~~~~~~~~~~~~~~~~~~~

Records a payment from the current user to another member.
Automatically marks any unsettled splits the payer owes the payee in that household as settled.

**Request body:**

.. code-block:: json

   {
     "household_id": 1,
     "payee_id": 2,
     "amount": 20.00,
     "note": "Owed from last week's shop"
   }

**Errors:** ``400`` if trying to pay yourself.

GET /api/payments/get/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a single payment's details.

DELETE /api/payments/delete/<id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deletes a payment record. Only the payer or an admin can delete.

Known Limitations
-----------------

- The ``/api/posts`` endpoints are placeholders and not yet implemented.
- No rate limiting or API versioning is implemented.
- All monetary amounts are returned as strings to avoid floating point issues.
