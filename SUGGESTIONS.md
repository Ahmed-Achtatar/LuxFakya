# Suggested Improvements for LuxFakia Website

Based on a review of the current codebase, the following improvements are recommended to enhance stability, functionality, security, and maintainability.

## 1. Code Quality & Maintenance

### Fix Deprecations
- **SQLAlchemy 2.0 Compatibility**: Replace `Model.query.get(id)` with `db.session.get(Model, id)` in `app.py`, `routes.py`, and `tests.py`.
- **Datetime**: Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` in `models.py` to ensure timezone awareness and future compatibility.

### Database Schema Refactoring
- **Category Foreign Key**: Currently, `Product` links to `Category` via a string name (`category` column). This should be changed to a Foreign Key (`category_id`) referencing `Category.id`. This ensures data integrity and allows for automatic updates if a category name changes.
- **Hardcoded Secrets**: The `SECRET_KEY` in `app.py` has a default fallback. Ensure this is strictly managed via environment variables in production, and consider removing the fallback to fail fast if missing.

### Refactoring
- **Centralize Pricing Logic**: The logic for calculating product prices (checking tiered `ProductPricing`) is duplicated in the `cart` route and the `checkout` route. Move this into a method on the `Product` model (e.g., `get_price_for_quantity(qty)`) or a dedicated service to ensure consistency and reduce code duplication.

## 2. Functionality & Features

### Search Functionality
- **Implement Search**: The mobile navbar includes a search form that sends a `q` parameter to the `/shop` route, but the backend currently ignores it. Update the `shop` view function in `routes.py` to filter products based on this query.

### Broken/Placeholder Links
- **Navbar Links**: Links for "Recipes", "Blog", and "Contacts" currently point to `#`. Either implement these pages or hide the links until they are ready.
- **Footer Links**: Many footer links (e.g., "Returns", "Shipping", "Terms") are placeholders. Create simple text pages for these or link them to the About page anchor points.

### Contact Form
- **Interactive Form**: The `/about` page displays contact info but lacks a submission form. Implement a working contact form (using Flask-WTF) to allow users to send messages directly from the website.

## 3. UI/UX & Design

### External Dependencies
- **Asset Vendoring**: The `base.html` template relies on external CDNs (Bootstrap, FontAwesome, AOS). Consider downloading these assets to the `static/` folder to improve load times, privacy, and offline development capabilities.
- **Footer Images**: The App Store/Google Play images in the footer link to `xstore.b-cdn.net`. These should be replaced with local assets or official badges to prevent broken images if the external host goes down.

### SEO & Accessibility
- **Meta Tags**: Add `<meta name="description">` and `<meta name="keywords">` tags to `base.html` (dynamically populated from templates) to improve Search Engine Optimization.
- **Alt Text**: Ensure all images, especially product images and the logo, have descriptive `alt` attributes for screen readers.

## 4. Security

### Rate Limiting
- **Protect Endpoints**: Add `Flask-Limiter` to rate-limit sensitive endpoints like `/admin/login` and `/checkout` to prevent brute-force attacks or spam.

## 5. Infrastructure

### Testing
- **Test Suite Structure**: Split `tests.py` into a package (e.g., `tests/test_routes.py`, `tests/test_models.py`) to make the test suite more manageable as the application grows.
- **Assertion Improvements**: Use string decoding in tests (e.g., `response.text`) instead of checking bytes (`response.data`) for cleaner test code.

### Database Seeding
- **Non-Destructive Seeding**: The current `seed.py` drops all tables (`db.drop_all()`). Create a separate command for "resetting" the database vs. "seeding" new data, or modify `seed.py` to check for existing data before insertion to prevent accidental data loss in production.
