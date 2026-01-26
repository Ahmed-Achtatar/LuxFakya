from app import create_app
from models import db, Product, Category

app = create_app()

def update_units():
    with app.app_context():
        target_categories = [
            'Dattes (تمور)',
            'Fruits secs / fruits à coque (مكسرات / فاكية)',
            'Fruits confits (فواكه معسلة)',
            'Fruits lyophilisés (فواكه مجففة بالتبريد)'
        ]

        print("Starting unit update...")

        updated_count = 0

        for cat_name in target_categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                print(f"Category not found: {cat_name}")
                continue

            products = Product.query.filter_by(category_id=category.id).all()
            for product in products:
                # Normalize unit to 'Kg'
                if product.unit != 'Kg':
                    print(f"Updating product '{product.name}': Unit '{product.unit}' -> 'Kg'")
                    product.unit = 'Kg'
                    updated_count += 1

        if updated_count > 0:
            db.session.commit()
            print(f"Successfully updated {updated_count} products.")
        else:
            print("No products needed updating.")

        print("Unit update complete.")

if __name__ == "__main__":
    update_units()
