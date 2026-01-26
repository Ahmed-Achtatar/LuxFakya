from app import create_app
from models import db, ProductPricing, Product
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        # 1. Add Column
        print("Adding display_unit column to product_pricing table...")
        try:
            with db.engine.connect() as conn:
                # Check if column exists first to avoid error spam (optional, but good practice)
                # But simple try/except is fine for this task
                conn.execute(text("ALTER TABLE product_pricing ADD COLUMN display_unit VARCHAR(20) DEFAULT 'Kg'"))
                conn.commit()
            print("Column added successfully.")
        except Exception as e:
            print(f"Column addition failed (might already exist or other error): {e}")

        # 2. Migrate Data
        print("Migrating data...")
        # Now that the column exists, we can use the ORM
        pricings = ProductPricing.query.all()
        count = 0
        for p in pricings:
            product = Product.query.get(p.product_id)
            if product:
                # Check if unit is Kg (case insensitive) and quantity < 1
                if product.unit and product.unit.lower() == 'kg' and p.quantity < 1.0:
                    p.display_unit = 'g'
                    count += 1
                else:
                    # Default is 'Kg' from schema, but let's be explicit
                    # If product.unit is 'pcs', display_unit should probably be 'pcs'?
                    # But the requirement is specifically about Kg -> g conversion.
                    # For non-Kg products, display_unit can default to 'Kg' (unused) or match product unit?
                    # ProductPricing doesn't enforce unit match.
                    # Let's default to 'Kg' as per model definition, or maybe None?
                    # Model default is 'Kg'.
                    # If product unit is 'pcs', quantity 1.0. display_unit='Kg'.
                    # Display logic: if display_unit=='Kg' -> show quantity + "Kg".
                    # This would show "1 Kg" for a "pcs" product if we blindly use display_unit.
                    # Current plan for templates: use display_unit IF SET?
                    # Or always?
                    # If I set display_unit to 'Kg', then non-Kg products will show 'Kg'.
                    # FIX: If product unit is NOT Kg, we should probably set display_unit to product.unit?
                    # But the task is specifically about the Kg/g split.
                    # Let's update the logic:
                    if product.unit and product.unit.lower() != 'kg':
                        p.display_unit = product.unit
                    else:
                        p.display_unit = 'Kg' # Default for Kg items >= 1.0

        db.session.commit()
        print(f"Migrated {count} records to 'g'.")

if __name__ == "__main__":
    migrate()
