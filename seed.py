from app import create_app
from models import db, User, Product
import os

app = create_app()

def seed():
    with app.app_context():
        # Drop all tables to start fresh
        db.drop_all()
        db.create_all()

        # Check if admin exists
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('password123')
            db.session.add(user)
            print("Admin user created (admin/password123)")

        # Verified Unsplash URLs
        dates_url = "https://images.unsplash.com/photo-1679949499517-1ce03d17f20b?auto=format&fit=crop&w=800&q=80"
        almonds_url = "https://images.unsplash.com/photo-1756361947189-29e0baae7bcd?auto=format&fit=crop&w=800&q=80"
        walnuts_url = "https://images.unsplash.com/photo-1644245903028-9b184b04e59e?auto=format&fit=crop&w=800&q=80"
        mix_url = "https://images.unsplash.com/photo-1722109998479-461ba34cd75a?auto=format&fit=crop&w=800&q=80"

        # Fallback/Generic URLs (using the ones we found as base)
        # Using the mix for gift boxes, walnuts for other nuts, dates for dried fruits

        products = [
            # Dates
            Product(
                name="Premium Mejhoul Dates",
                description="The king of dates, sweet and succulent.",
                price=25.00,
                category="Dates",
                image_url=dates_url
            ),
            Product(
                name="Deglet Nour Dates",
                description="Translucent color and a soft honey-like taste.",
                price=15.00,
                category="Dates",
                image_url=dates_url
            ),

            # Nuts
            Product(
                name="Roasted Almonds",
                description="Crunchy and salted roasted almonds.",
                price=18.00,
                category="Nuts",
                image_url=almonds_url
            ),
            Product(
                name="Premium Walnuts",
                description="High quality walnuts, rich in Omega-3.",
                price=22.00,
                category="Nuts",
                image_url=walnuts_url
            ),
            Product(
                name="Salted Pistachios",
                description="Deliciously salted pistachios in shell.",
                price=24.00,
                category="Nuts",
                image_url=mix_url # Using mix as fallback for pistachios
            ),
            Product(
                name="Roasted Cashews",
                description="Creamy and crunchy roasted cashews.",
                price=26.00,
                category="Nuts",
                image_url=mix_url # Using mix as fallback
            ),

            # Dried Fruits
            Product(
                name="Dried Apricots",
                description="Sweet and tangy dried apricots.",
                price=12.00,
                category="Dried Fruits",
                image_url=mix_url # Using mix
            ),
            Product(
                name="Dried Figs",
                description="Natural sweetness and chewy texture.",
                price=14.00,
                category="Dried Fruits",
                image_url=dates_url # Using dates as fallback for figs
            ),
            Product(
                name="Golden Raisins",
                description="Sweet golden raisins, perfect for snacking.",
                price=10.00,
                category="Dried Fruits",
                image_url=mix_url
            ),

            # Gift Boxes
            Product(
                name="Luxury Fakia Box",
                description="An assortment of our finest nuts and dried fruits.",
                price=55.00,
                category="Gift Boxes",
                image_url=mix_url
            ),
            Product(
                name="Dates Assortment Plateau",
                description="A beautiful arrangement of stuffed dates.",
                price=45.00,
                category="Gift Boxes",
                image_url=dates_url
            ),
            Product(
                name="Moroccan Tea Time Set",
                description="Perfect companion for Moroccan mint tea.",
                price=35.00,
                category="Gift Boxes",
                image_url=mix_url
            )
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        print(f"Database reset and seeded with {len(products)} products.")

if __name__ == '__main__':
    seed()
