# Deploying to Railway

Follow these steps to host your application on Railway.

## 1. Prepare Repository
Ensure your code is pushed to a GitHub repository.

## 2. Create Project on Railway
1.  Log in to [Railway.app](https://railway.app/).
2.  Click **New Project** -> **Deploy from GitHub repo**.
3.  Select your repository.
4.  Railway will automatically detect the Python environment and the `Procfile`.

## 3. Add a Database
1.  In your project canvas, right-click (or click "New") -> **Database** -> **PostgreSQL**.
2.  Wait for the database to be provisioned.
3.  Railway should automatically inject `DATABASE_URL` into your web service's environment variables.
    *   *Verification*: Click on your Web Service card -> **Variables**. You should see `DATABASE_URL` (usually linked to the Postgres service).

## 4. Configure Environment Variables
In your Web Service -> **Variables**:
1.  Add `SECRET_KEY`: Set this to a long random string for security.

## 5. Seed the Database
Your application automatically creates the database tables on startup, but they will be empty. To populate them with initial data (Categories, Products, Admin User):

**Option A: Using Railway CLI (Recommended)**
1.  Install the [Railway CLI](https://docs.railway.app/guides/cli).
2.  In your local terminal, run `railway login`.
3.  Run `railway link` and select your project.
4.  Run the seed script:
    ```bash
    railway run python seed.py
    ```

**Option B: Using the Deploy Command (Temporary)**
1.  Go to your Web Service -> **Settings** -> **Deploy**.
2.  Set the **Start Command** to `python seed.py && gunicorn wsgi:app`.
3.  Trigger a redeploy.
4.  Once deployed (and seeded), change the Start Command back to just `gunicorn wsgi:app` (or clear it to use the Procfile default) and redeploy.

## 6. Access Your App
Click on the provided Railway domain (e.g., `xxx.up.railway.app`) to view your live shop.
