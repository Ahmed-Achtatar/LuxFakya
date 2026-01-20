# Deployment Guide (Railway)

This guide outlines the steps to deploy the application to Railway.app.

## Prerequisites

*   A [GitHub](https://github.com/) account.
*   A [Railway](https://railway.app/) account.
*   The [Railway CLI](https://docs.railway.app/guides/cli) (optional, used for creating the initial admin account).

## Deployment Steps

1.  **Push to GitHub**: Ensure your code is pushed to your GitHub repository.

2.  **Create a New Project on Railway**:
    *   Go to your Railway dashboard.
    *   Click "New Project".
    *   Select "Deploy from GitHub repo".
    *   Select your repository.

3.  **Add a PostgreSQL Database**:
    *   In the project view, click "New" -> "Database" -> "PostgreSQL".
    *   Railway will automatically link this database to your application (providing the `DATABASE_URL` variable).

4.  **Configure Environment Variables**:
    *   Click on your application service (the GitHub repo card).
    *   Go to the "Variables" tab.
    *   Add `SECRET_KEY` with a strong random string.

5.  **Verify Deployment**:
    *   Railway will automatically detect the `Procfile` and `requirements.txt`.
    *   The application handles database table creation automatically on startup.
    *   Go to "Settings" -> "Networking" to generate or view your public domain.

## Database Initialization (Create Admin User)

The application starts with an empty database. You need to create the initial Admin account to log in and start populating content.

**Option 1: Using Railway CLI (Recommended)**

1.  Install Railway CLI: `npm i -g @railway/cli`
2.  Login: `railway login`
3.  Link your project: `railway link` (Select your project)
4.  Run the seed script:
    ```bash
    railway run python seed.py
    ```
    This script will check if an admin exists. If not, it creates one with:
    *   **Username:** `admin`
    *   **Password:** `password123`

**Option 2: Using Railway Console**

1.  Go to your project in the Railway Dashboard.
2.  Click on your application service.
3.  Go to the "Settings" tab.
4.  Scroll down to "Service Command" (or "Start Command").
5.  Change it temporarily to: `python seed.py && gunicorn wsgi:app`
6.  Redeploy.
7.  Check the logs to see "Admin user created".
8.  **Revert** the start command to empty (or `gunicorn wsgi:app`) and redeploy.

## Post-Deployment

1.  Log in at `/login` with the admin credentials.
2.  **Change your password immediately.**
3.  Go to the Admin Dashboard to add Categories and Products.
