# Website Problems Report

Based on the codebase analysis, the following issues have been identified:

## 1. Logic & Functionality

### 1.1. Unreliable Float Comparison in Cart Logic
- **Location:** `routes.py` (functions `cart`, `checkout`), `app.py` (`inject_global_context`).
- **Issue:** The code uses `==` to compare floating-point numbers (`pricing.quantity == quantity`). Due to floating-point precision (e.g., `0.1 + 0.2 != 0.3`), this check can fail even for valid quantities, causing the system to fall back to the base price instead of the discounted tier price.
- **Impact:** Users might be charged the wrong amount if they add multiple small quantities that sum up to a tier but don't match exactly due to precision.

### 1.2. "Quick Add" Logic Flaw
- **Location:** `templates/product_detail.html` (Related Products section).
- **Issue:** The "Quick Add" button sends a GET request to `/cart/add/<id>` without a quantity parameter, defaulting to `1.0`.
- **Impact:** If a product is sold *only* in small packs (e.g., 250g) and has no pricing defined for 1.0 unit (1kg), adding 1.0 will fall back to the base price calculation. This might bypass the intended sales units (e.g. user buys 1kg of Saffron instead of 1g).

### 1.3. Price Recalculation at Checkout
- **Location:** `routes.py` (`checkout` function).
- **Issue:** Prices are recalculated at the moment of checkout based on current DB values, not the values at the time they were added to the cart.
- **Impact:** If an admin changes the price while a user is browsing, the user might see one price in the cart and be charged another at checkout without warning.

### 1.4. Race Conditions in Stock Management
- **Location:** `routes.py` (`checkout` function).
- **Issue:** The checkout process checks `is_out_of_stock` but does not atomically decrement stock (if stock tracking were implemented beyond a boolean) or lock the row.
- **Impact:** Two users could theoretically buy the last item simultaneously.

## 2. Performance

### 2.1. N+1 Query Problem in Cart
- **Location:** `app.py` (`inject_global_context`), `routes.py` (`cart`).
- **Issue:** The code iterates over `cart` items and accesses `product.pricings` for each. Since `pricings` is lazy-loaded, this triggers a separate SQL query for *every* product in the cart on *every* page load (because `inject_global_context` runs for the cart badge/total).
- **Impact:** Performance degradation as cart size increases.

## 3. Database & Schema

### 3.1. Ad-hoc Schema Migration
- **Location:** `fix_db.py`.
- **Issue:** The application runs a custom schema fix script (`run_db_fix`) on every startup. It manually checks for columns and adds them using raw SQL.
- **Impact:** This is fragile and risky compared to a proper migration tool (e.g., Alembic). It can lead to race conditions during deployment or inconsistent schema states.

### 3.2. Legacy SQLAlchemy Methods
- **Location:** Multiple files (`app.py`, `routes.py`).
- **Issue:** Usage of deprecated methods like `Query.get()` (should be `Session.get()`) and `datetime.utcnow()` (should be timezone-aware).
- **Impact:** Future compatibility issues with SQLAlchemy 2.0 and Python updates.

## 4. Security

### 4.1. Hardcoded Secrets
- **Location:** `app.py`.
- **Issue:** `app.config['SECRET_KEY']` falls back to a hardcoded string `'dev-secret-key-luxfakia'` if the environment variable is missing.
- **Impact:** If deployed without the env var, sessions could be signed with a known key, allowing attackers to forge session cookies.

### 4.2. Input Validation
- **Location:** `routes.py` (`add_to_cart`).
- **Issue:** The `quantity` parameter is cast to `float` but not validated against allowed increments or pricing tiers.
- **Impact:** A malicious user could add arbitrary quantities (e.g., `0.0001`) to the cart, potentially causing rounding errors or exploiting pricing logic.
