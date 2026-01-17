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
    *   In the project view, right-click (or click "New") to add a service.
    *   Select "Database" -> "PostgreSQL".
    *   This will automatically create a `DATABASE_URL` environment variable available to your application service.

4.  **Configure Environment Variables**:
    *   Click on your application service (the GitHub repo).
    *   Go to the "Variables" tab.
    *   Add `SECRET_KEY` with a strong random string.
    *   (Optional) If you have other variables (e.g., mail settings), add them here.

5.  **Verify Deployment**:
    *   Railway will automatically detect the `Procfile` and `requirements.txt`.
    *   Watch the "Deployments" logs to ensure the build and start up are successful.
    *   Once deployed, a public URL will be generated (you might need to enable it in the "Settings" -> "Networking" tab).

## Database Initialization

After the first deployment, you need to initialize the database tables and seed initial data.

**Using Railway CLI:**

1.  Install Railway CLI: `npm i -g @railway/cli`
2.  Login: `railway login`
3.  Link your project: `railway link`
4.  Run the seed script:
    ```bash
    railway run python seed.py
    ```
    *Note: `seed.py` uses `app.app_context()` so it will use the `DATABASE_URL` from the environment.*

**Alternatively (if CLI is not an option):**

You can modify the `Start Command` in the "Settings" tab of your service temporarily to:
```bash
python seed.py && gunicorn wsgi:app
```
Deploy once, then change it back to just `gunicorn wsgi:app` (or leave it empty to default to Procfile). Note that `seed.py` might reset data if not careful, so check the script logic.

## Troubleshooting

*   **Logs**: Check the "Deploy Logs" and "App Logs" in the Railway dashboard.
*   **Database Connection**: Ensure the PostgreSQL service is in the same project and environment.
