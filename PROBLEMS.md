# Identified Problems

## Security
1. **Hardcoded Secret Key**: `app.py` sets `app.config['SECRET_KEY']` to `'dev-secret-key-luxfakia'` if the environment variable is not set. This is a security risk if the environment variable is accidentally omitted in production.
2. **Debug Mode in Entry Point**: `app.py`'s `if __name__ == '__main__':` block runs `app.run(debug=True)`. While `wsgi.py` exists for production, executing `app.py` directly in a production environment would expose the debugger.
3. **Git History Pollution**: `app.log` is tracked in git (present in file list) and not ignored in `.gitignore` (which only ignores `flask.log`). This may leak sensitive runtime information.
4. **Missing Security Headers**: No explicit configuration for `Secure`, `HttpOnly`, or `SameSite` attributes on session cookies, nor Content Security Policy (CSP) headers.

## Code Quality & Deprecations
1. **SQLAlchemy Deprecations**: The codebase frequently uses `Model.query.get(id)` (e.g., `User.query.get`, `Product.query.get`), which triggers `LegacyAPIWarning` in SQLAlchemy 2.0. This should be replaced with `db.session.get(Model, id)`.
2. **Datetime Deprecation**: `models.py` uses `datetime.utcnow`, which is deprecated in Python 3.12. It should be replaced with `datetime.now(datetime.timezone.utc)`.
3. **Inefficient Data Loading**: In `routes.py`, the `index` route fetches `Product.query.all()` (all products) and then slices the list in Python. As the database grows, this will become a significant performance bottleneck.

## Data Integrity
1. **Loose Schema Relations**: `Product.category` is defined as a `String` column rather than a Foreign Key to the `Category` model. This allows for typos (e.g., "Dates" vs "dates") and makes renaming categories difficult.
2. **Missing Foreign Key on Order Items**: `OrderItem.product_id` is an integer column without a Foreign Key constraint to the `Product` table. While this might be intentional to preserve order history if a product is deleted, it lacks referential integrity.

## Frontend & UX
1. **Dead Links**: The footer in `templates/base.html` contains multiple placeholder links (`#`) under "Our Story" (e.g., Company Profile, Facility) and "Support" (e.g., Order Status, Returns).
2. **Hardcoded External Links**: The Google Maps link in `templates/base.html` has hardcoded coordinates.
3. **Inline JavaScript**: `templates/base.html` contains inline JavaScript for AOS initialization and Toast handling, which is harder to maintain than external scripts.

## Dependencies & Environment
1. **Missing Dev Dependencies**: `playwright` is required for verification scripts (according to context) but is missing from `requirements.txt`.
2. **Database Driver**: `psycopg2-binary` is used, which is generally recommended for development/testing but `psycopg2` (built from source) is often preferred for production performance and stability.
