# Deploying to Railway

This guide outlines the steps to deploy the application to Railway.app.

## Prerequisites

*   A [GitHub](https://github.com/) account.
*   A [Railway](https://railway.app/) account.

## Deployment Steps

1.  **Push to GitHub**: Ensure your code is pushed to a GitHub repository.

2.  **Create a New Project on Railway**:
    *   Go to your Railway dashboard.
    *   Click "New Project".
    *   Select "Deploy from GitHub repo".
    *   Select your repository.

3.  **Add a PostgreSQL Database (REQUIRED)**:
    *   **CRITICAL STEP**: By default, the app uses SQLite which loses data on every restart in Railway. You **MUST** add a PostgreSQL service.
    *   In the project view, click "New" -> "Database" -> "PostgreSQL".
    *   Railway will automatically link this database to your application by setting the `DATABASE_URL` environment variable.

4.  **Configure Environment Variables**:
    *   Click on your application service.
    *   Go to the "Variables" tab.
    *   Add `SECRET_KEY` with a strong random string.

5.  **Verify Deployment**:
    *   The application includes **Auto-Seeding**. On the first run with a fresh database, it will automatically populate default products and the admin user.
    *   Watch the "Deployments" logs. You should see "Auto-seeding completed successfully".
    *   Once deployed, a public URL will be generated (enable it in "Settings" -> "Networking").
    *   **Admin Login**: `admin` / `password123`

## Troubleshooting

### "The website opens but there are no products"
*   **Cause**: You might still be using SQLite (no Postgres service added), or the auto-seeder failed.
*   **Fix**:
    1.  Ensure you have a PostgreSQL service added in your Railway project.
    2.  Check the logs for "WARNING: No DATABASE_URL found". If you see this, you missed Step 3.
    3.  Check the logs for "ERROR: Auto-seeding failed".

### "Application Error" or 500
*   **Cause**: Database connection failed or code error.
*   **Fix**:
    1.  Click on the "Deployments" tab and "View Logs".
    2.  Look for "CRITICAL: Database connection failed".
    3.  Visit `https://your-app-url/health` to see the error message.

### "Deploy Failed"
*   **Cause**: Build error.
*   **Fix**: Check the "Build Logs". Ensure `requirements.txt` is present and valid.

## Manual Seeding (Optional)

If you need to reset the database manually (WARNING: Deletes all data), you can use the Railway CLI:

```bash
railway run python seed.py
```
