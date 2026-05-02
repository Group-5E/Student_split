Backend API 
===========

This page documents the current backend API for **Student Split**.
The backend is built using Flask and exposes JSON-based endpoints for authentication and post interactions.

Authentication Model 
--------------------

The backend uses **Flask Login** for session-based authentication.

- When  a user logs in or registers, Flask-Login creates a **secure session cookie**.
- Clients retain this cookie to remain authenticated.
- Protected endpoints require the cookie to be sent automatically by the HTTP client.

Authentication Endpoints 
------------------------

These endpoints are registered under the ``auth_bp`` blueprint.

POST /register 
--------------

Details coming soon.

POST /login 
-----------

Details coming soon.

POST /logout 
------------

Details coming soon.

Post Endpoints 
--------------

These endpoints are registered under the ``posts_bp`` blueprint.

POST /hello 
-----------

Details coming soon.

POST /create 
------------

Details coming soon.

GET /getLatest 
--------------

Details coming soon.

Problems
--------

- The ``/create`` and ``/getLatest`` are placeholders and require updating for full functionality.
- No authorisation rules exist yet (all users have equal access).
- No rate limiting or versioning is implemented.