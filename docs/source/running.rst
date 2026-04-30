
Running the Application
=======================

Once installation is done, you can move on and run the backend and frontend.
This page explains how to start both.

Backend (Flask)
---------------

Start the backend from the ``backend`` directory::

    cd backend
    flask run 

By default, the backend will run on:
http://127.0.0.1:5000 
OR 
http://127.0.0.1 in Bing

Frontend (React + pnpm)
-----------------------

Start the frontend from the ``frontend`` directory::

    cd frontend 
    pnpm run dev 

The frontend typically runs on:
http://localhost:5173 

Running Both Together 
---------------------

To run the whole application altogether:

1. Open **two terminals**
2. In Terminal 1, start the backend 
3. In Terminal 2, start the frontend 

The frontend will communicate with the backend as long as both are running, and you won't have to intervene.

Changing Ports or API URLs
--------------------------

If you change the backend port or host, update the frontend to reflect that.

Troubleshooting
---------------

- **Backend not responding**
  Make sure the virtual environment is active and Flask is running on the right port.

- **Frontend cannot reach the backend**
  Check the URL in your frontend configuration.

- **Port already in use**
  Either stop any other development you are running on that port, or change the port in your configuration of the project.

- **CORS or network errors**
  Confirm both services are running on the correct ports and that the backend is reachable.

Next Steps
----------

- :doc:`backend_api` - Learn about the backend API 
- :doc:`project_structure` - Understand how the repository is organised