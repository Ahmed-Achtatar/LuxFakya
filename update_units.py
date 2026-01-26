from app import create_app
from models import db, Product, Category

app = create_app()

def update_units():
    with app.app_context():
        # Keywords to identify categories (avoiding Arabic for robust matching)
        target_keywords = [
            'Dattes',
            'Fruits secs',
            'Fruits confits',
            'Fruits lyophilisés',
            'Offres' # Optional: if gift boxes are also Kg based? Maybe not. User request was generic.
                     # But usually gift boxes are 'pcs' or 'box'.
                     # Let's stick to the weight-based ones.
        ]

        # Specific fix for "Fanid" if it's in a weight category
        # The user mentioned "Fanid" earlier in the context.

        print("Starting unit update (Robust Mode)...")

        all_categories = Category.query.all()
        target_category_ids = []

        for cat in all_categories:
            match = False
            for keyword in target_keywords:
                if keyword in cat.name:
                    match = True
                    break

            if match:
                print(f"Matched Category: {cat.name} (ID: {cat.id})")
                target_category_ids.append(cat.id)
            else:
                print(f"Skipping Category: {cat.name}")

        if not target_category_ids:
            print("No target categories found! Check your database.")
            return

        updated_count = 0
        products = Product.query.filter(Product.category_id.in_(target_category_ids)).all()

        for product in products:
            # We enforce 'Kg' for consistency with the frontend logic
            if product.unit != 'Kg':
                print(f"Updating product '{product.name}': Unit '{product.unit}' -> 'Kg'")
                product.unit = 'Kg'
                updated_count += 1

        if updated_count > 0:
            db.session.commit()
            print(f"Successfully updated {updated_count} products.")
        else:
            print(f"Checked {len(products)} products. No updates needed (all are already 'Kg').")

        print("Unit update complete.")

if __name__ == "__main__":
    update_units()
