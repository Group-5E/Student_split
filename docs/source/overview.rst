Overview
========

Student Split is a full-stack web-based application designed to streamline the process of planning, organising and managing household expenses, as well as splitting household tasks.
The project is build using a modern, streamlined frontend powered by **pnpm** and a backend implemented with **Flask**.

This page is designed to give a high-level understanding of the system, its purpose, and how everything fits together.

Purpose
-------

Student Split aims to provide a simple and intuitive platform for:

- Managing shared tasks and responsibilities
- Coordinating expenses between a household
- Providing a clean interface for backend data

Architecture
------------

The project follows a lightweight, developer-friendly **n-tier architecture**. This helps improve scalability and allows multiple developers to work simultaneously:

- **Frontend (Presentation Tier)**
    Built with modern JavaScript tooling, https://react.dev/ and managed using ``pnpm``.
    It handles all user-facing interactions, UI components, and API requests.

- **Backend (Application Tier)**
    A Python Flask application that handles data processing and manages server-side logic.

- **API**
    The frontend communicates with the backend via HTTP requests.
    This seperation allows each part of the system to be developed and deployed independently.

High-Level Structure
--------------------

The repository is organised into two main components:
- ``frontend/`` - Contains the client-side application and dependencies.
- ``backend/`` - Contains the Flask application, routes, models and environment setup.

A more detailed breakdown of the folder layout cna be found in the :doc:`project_structure` section.

Key Features
------------

- Clear seperation between frontend and backend
- Simple setup process for developers or potential contributors
- Lightweight and easy to expand
- Uses modern tooling (pnpm, virtual environments, Flask, ReactJS)
- Designed for collaborative student workflows

Next Steps
----------

If you're new to the project, start with:

1. :doc:`installation` - Set up the environment
2. :doc:`running` - Learn how to run the frontend and backend together
3. :doc:`backend_api` - Learn about the backend API