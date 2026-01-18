# Deploying to Railway

This guide outlines the steps to deploy the application to Railway.app.

## Prerequisites

*   A [GitHub](https://github.com/) account.
*   A [Railway](https://railway.app/) account.
*   The [Railway CLI](https://docs.railway.app/guides/cli) (optional, but useful for seeding).

## Deployment Steps

1.  **Push to GitHub**: Ensure your code is pushed to a GitHub repository.

2.  **Create a New Project on Railway**:
    *   Go to your Railway dashboard.
    *   Click "New Project".
    *   Select "Deploy from GitHub repo".
    *   Select your repository.

3.  **Add a PostgreSQL Database**:
    *   **CRITICAL STEP**: By default, the app uses SQLite which loses data on every restart in Railway. You **MUST** add a PostgreSQL service.
    *   In the project view, click "New" -> "Database" -> "PostgreSQL".
    *   Railway will automatically link this database to your application by setting the `DATABASE_URL` environment variable.

4.  **Configure Environment Variables**:
    *   Click on your application service.
    *   Go to the "Variables" tab.
    *   Add `SECRET_KEY` with a strong random string (e.g., generated via `openssl rand -hex 32`).

5.  **Verify Deployment**:
    *   Watch the "Deployments" logs.
    *   Once deployed, a public URL will be generated (enable it in "Settings" -> "Networking").
    *   Visit `/health` on your deployed URL (e.g., `https://your-app.up.railway.app/health`) to verify the database connection.

## Database Initialization (Seeding)

After the deployment is successful (green checkmark), your database is empty. You need to seed it.

**Method A: Using Railway CLI (Recommended)**

1.  Install Railway CLI: `npm i -g @railway/cli`
2.  Login: `railway login`
3.  Link your project: `railway link`
4.  Run the seed script:
    ```bash
    railway run python seed.py
    ```

**Method B: Using the "Start Command" Trick**

If you cannot use the CLI:

1.  Go to your App Service "Settings".
2.  Change "Start Command" to:
    ```bash
    python seed.py && gunicorn wsgi:app
    ```
3.  Redeploy. The app will seed the database on startup.
4.  **Important**: Once verified that products appear, change the "Start Command" back to empty (or `gunicorn wsgi:app`) to avoid re-seeding on every restart (though the script is safe, it resets data).

## Troubleshooting

### "The website opens but there are no products"
*   **Cause**: The database has not been seeded, or you are using SQLite (no Postgres service).
*   **Fix**:
    1.  Ensure you have a PostgreSQL service added in your Railway project.
    2.  Check the "Variables" tab of your app service. Do you see `DATABASE_URL`?
    3.  Run the seed script (see above).
    4.  Check the logs. If you see "WARNING: No DATABASE_URL found", you missed Step 3.

### "Application Error" or 500
*   **Cause**: Database connection failed or code error.
*   **Fix**:
    1.  Click on the "Deployments" tab and "View Logs".
    2.  Look for "CRITICAL: Database connection failed".
    3.  If you see connection errors, ensure the Postgres service is healthy.
    4.  Visit `https://your-app-url/health` to see the error message.

### "Deploy Failed"
*   **Cause**: Build error.
*   **Fix**: Check the "Build Logs". Ensure `requirements.txt` is present and valid.
