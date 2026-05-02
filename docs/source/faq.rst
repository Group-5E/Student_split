FAQ
===

This page answers common questions about **Student Split**, covering the backend, frontend and documentation.

General Questions
-----------------

What is Student Split
~~~~~~~~~~~~~~~~~~~~~

Student Split is a full-stack application designed to help students manage shared expenses, track household bill payments, and organise household finances.
It consists of a Flask backend, a ReactJS frontend, and Sphinx-based documentation.

Who is this project for
~~~~~~~~~~~~~~~~~~~~~~~

Whilst this project is still undergoing development, it is mostly intended for potential developers and anyone interested in learning how a modern full-stack application is structured.

Backend Questions
-----------------

Why Flask instead of anything else
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask provides a lightweight, flexible foundation that fits the project's size.
It allows contributors to understand the backend without navigating a large framework.

How does the authentication work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Authentication uses **Flask Login** with session cookies.

- When a user logs in or registers, a session cookie is created.
- The cookie must be preserved by the client, else they won't be authenticated.

Where is the database stored
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Details coming soon.

Frontend Questions
------------------

Why Vite instead of something else
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vite provides:

- Faster development server startup
- Better TypeScript support
- Modern tooling with minimal configuration

Where do I add new pages or components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Frontend structure:

- Components -> ``frontend/src/components``
- Hooks -> ``frontend/src/hooks``
- Routes -> ``frontend/src/routes``
- Styles -> ``frontend/src/styles``