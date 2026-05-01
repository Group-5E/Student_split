Project Structure
=================

This page explains how the project is organised. The project follows an n-tier architecture with a clear seperation between the **backend**, **frontend**, and **documentation**.

Repository Layout
-----------------

Below is the high-level structure of the project::

    student-split/
      ├── backend/
      │   ├── .venv/
      │   ├── instance/
      │   │   └── app.db
      │   ├── project/
      │   │   ├── models/
      │   │   │   ├── base.py
      │   │   │   ├── expenses.py
      │   │   │   ├── households.py
      │   │   │   ├── payment.py
      │   │   │   ├── users.py
      │   │   │   └── views.py
      │   │   └── routes/
      │   │       ├── auth.py
      │   │       ├── posts.py
      │   │       └── settings.py
      │   ├── app.py
      │   ├── .gitignore
      │   └── requirements.txt
      │
      ├── frontend/
      │   ├── public/
      │   ├── src/
      │   │   ├── components/
      │   │   ├── hooks/
      │   │   ├── lib/
      │   │   ├── routes/
      │   │   └── styles/
      │   ├── index.html
      │   ├── package.json
      │   ├── pnpm-lock.yaml
      │   ├── tsconfig.json
      │   └── vite.config.ts
      │
      ├── docs/
      │   ├── source/
      │   │   ├── overview.rst
      │   │   ├── installation.rst
      │   │   ├── running.rst
      │   │   ├── project_structure.rst
      │   │   ├── backend_api.rst
      │   │   ├── contributing.rst
      │   │   └── conf.py
      │   ├── build/
      │   └── requirements.txt
      │
      ├── README.md
      └── .readthedocs.yaml

Backend Structure
-----------------
Details coming soon.

Frontend Structure
------------------
Details coming soon.

Documentation Structure
-----------------------
Details coming soon.

Root Files
----------
Details coming soon.

How This Supplements the Architecture
-------------------------------------
Details coming soon.

Next Steps
----------

- :doc:`running` - Learn how to run the application 
- :doc:`backend_api` - Learn about the backend API