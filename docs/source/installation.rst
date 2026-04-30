Installation 
============

This guide walks you through setting up the Student Split development environment, which includes setting up the frontend and the backend.
The project uses **pnpm** for the frontend and **Flask** for the backend, following an n-tier architecture.

Before Starting
---------------

Install the following:

- **Python 3.12+**
- **pip**
- **Node.js 18+**
- **pnpm**
- **Git**

If you already have these installed, verify the versions of each with:
`python --version`
`node --version`
`pnpm --version`

Backend Setup (Flask)
--------------------

1. Navigate to the backend directory:
`cd backend`

2. Create a virtual environment:
`python -m venv .venv`

3. Activate the virtual environment:
- **Windows**
`.venv\Scripts\activate`

- **macOS/Linux**
`source .venv/bin/activate`

4. Install backend packages:
`pip install -r requirements.txt`

Frontend Setup (pnpm + React)
----------------------------

1. Navigate to the frontend directory
`cd frontend`

2. Install pnpm:
`pnpm install`

3. Make sure you can run the server:
`pnpm run dev`

Running the Application
-----------------------

Once you have completed the above steps, do the following:

- Start the **backend**:
`flask run`

- Start the **frontend**:
`pnpm run dev`

The frontend will communicate with the backend through the configured API 

Troubleshooting
---------------

- If anything fails to install, ensure your Node and Python versions are correct, as listed above.
- If the backend does not start, ensure your virtual environment is active.
- If the frontend cannot reach the backend, check the API URL in your config.

Once installation is complete, visit one of the following pages:

- :doc:`running` - Learn how to run both services together
- :doc:`project_structure` - Understand the organisation of the repository
- :doc:`backend_api` - Learn about the backend API 
