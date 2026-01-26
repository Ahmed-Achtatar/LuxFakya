from app import create_app
from models import db, ProductPricing, Product
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        # 1. Add Column (Idempotent check)
        print("Checking/Adding display_unit column to product_pricing table...")
        try:
            with db.engine.connect() as conn:
                # We attempt to add the column. If it exists, it might fail or we catch it.
                # However, since we are using SQLite in dev and Postgres in prod,
                # a better way is to check if it exists or just catch the error.
                # Given the context, catching the error is simple and effective.
                conn.execute(text("ALTER TABLE product_pricing ADD COLUMN display_unit VARCHAR(20) DEFAULT 'Kg'"))
                conn.commit()
                print("Column added successfully.")
        except Exception:
            # Column likely exists
            print("Column 'display_unit' already exists or could not be added.")

        # 2. Migrate Data
        print("Migrating data...")
        pricings = ProductPricing.query.all()
        count_g = 0
        count_kg = 0
        count_other = 0

        for p in pricings:
            product = db.session.get(Product, p.product_id)
            if product:
                # Normalize unit comparison
                product_unit = product.unit.lower() if product.unit else 'pcs'

                if product_unit == 'kg':
                    if p.quantity < 1.0:
                        if p.display_unit != 'g':
                            p.display_unit = 'g'
                            count_g += 1
                    else:
                        # Ensure it is Kg for >= 1.0
                        if p.display_unit != 'Kg':
                            p.display_unit = 'Kg'
                            count_kg += 1
                else:
                    # For non-Kg products, use the product's unit
                    if p.display_unit != product.unit:
                        p.display_unit = product.unit
                        count_other += 1

        db.session.commit()
        print(f"Migration complete.")
        print(f"Updated {count_g} records to 'g' (quantity < 1.0).")
        print(f"Updated {count_kg} records to 'Kg' (quantity >= 1.0).")
        print(f"Updated {count_other} records to custom unit.")

if __name__ == "__main__":
    migrate()
