from app import create_app
from models import db, User, Product, ProductPricing, Category
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

        # Seed Categories
        categories = ["Dates", "Nuts", "Dried Fruits", "Gift Boxes"]
        for cat_name in categories:
            c = Category(name=cat_name)
            db.session.add(c)
        db.session.commit()
        print(f"Seeded {len(categories)} categories.")

        # Local Image URLs
        dates_url = "/static/images/dates.png"
        nuts_url = "/static/images/nuts.png"
        dried_url = "/static/images/driedfood.png"
        gift_url = "/static/images/gift.png"

        # Products
        p1 = Product(
            name="Premium Mejhoul Dates",
            description="The king of dates, sweet and succulent.",
            price=25.00,
            unit="kg",
            category="Dates",
            image_url=dates_url
        )
        db.session.add(p1)

        p2 = Product(
            name="Deglet Nour Dates",
            description="Translucent color and a soft honey-like taste.",
            price=15.00,
            unit="kg",
            category="Dates",
            image_url=dates_url
        )
        db.session.add(p2)

        p3 = Product(
            name="Roasted Almonds",
            description="Crunchy and salted roasted almonds.",
            price=18.00,
            unit="kg",
            category="Nuts",
            image_url=nuts_url
        )
        db.session.add(p3)

        p4 = Product(
            name="Premium Walnuts",
            description="High quality walnuts, rich in Omega-3.",
            price=22.00,
            unit="kg",
            category="Nuts",
            image_url=nuts_url
        )
        db.session.add(p4)

        # Other products...
        products = [
            Product(
                name="Salted Pistachios",
                description="Deliciously salted pistachios in shell.",
                price=24.00,
                unit="kg",
                category="Nuts",
                image_url=nuts_url
            ),
            Product(
                name="Roasted Cashews",
                description="Creamy and crunchy roasted cashews.",
                price=26.00,
                unit="kg",
                category="Nuts",
                image_url=nuts_url
            ),
            Product(
                name="Dried Apricots",
                description="Sweet and tangy dried apricots.",
                price=12.00,
                unit="kg",
                category="Dried Fruits",
                image_url=dried_url
            ),
            Product(
                name="Dried Figs",
                description="Natural sweetness and chewy texture.",
                price=14.00,
                unit="kg",
                category="Dried Fruits",
                image_url=dried_url
            ),
            Product(
                name="Golden Raisins",
                description="Sweet golden raisins, perfect for snacking.",
                price=10.00,
                unit="kg",
                category="Dried Fruits",
                image_url=dried_url
            ),
            Product(
                name="Luxury Fakia Box",
                description="An assortment of our finest nuts and dried fruits.",
                price=55.00,
                unit="box",
                category="Gift Boxes",
                image_url=gift_url
            ),
            Product(
                name="Dates Assortment Plateau",
                description="A beautiful arrangement of stuffed dates.",
                price=45.00,
                unit="plateau",
                category="Gift Boxes",
                image_url=gift_url
            ),
            Product(
                name="Moroccan Tea Time Set",
                description="Perfect companion for Moroccan mint tea.",
                price=35.00,
                unit="set",
                category="Gift Boxes",
                image_url=gift_url
            )
        ]

        for p in products:
            db.session.add(p)

        db.session.commit()

        # Add Pricing for p1 (Mejhoul Dates)
        pricings = [
            ProductPricing(product_id=p1.id, quantity=1.0, price=25.00),
            ProductPricing(product_id=p1.id, quantity=2.0, price=45.00),
            ProductPricing(product_id=p1.id, quantity=3.0, price=65.00)
        ]

        # Add Pricing for p2
        pricings.extend([
            ProductPricing(product_id=p2.id, quantity=1.0, price=15.00),
            ProductPricing(product_id=p2.id, quantity=2.0, price=28.00),
            ProductPricing(product_id=p2.id, quantity=3.0, price=40.00)
        ])

        for pr in pricings:
            db.session.add(pr)

        db.session.commit()
        print(f"Database reset and seeded with {Product.query.count()} products and {ProductPricing.query.count()} pricing tiers.")

if __name__ == '__main__':
    seed()
