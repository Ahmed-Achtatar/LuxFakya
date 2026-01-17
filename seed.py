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

        products = [
            Product(
                name="Organic Cayenne Powder",
                description="High quality organic cayenne powder.",
                price=9.99,
                category="Spices",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-1-min-300x300.jpg"
            ),
            Product(
                name="Madras Curry Powder",
                description="Authentic Madras Curry Powder.",
                price=30.99,
                category="Spices",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-2-min-300x300.jpg"
            ),
            Product(
                name="Cinnamon Powder",
                description="Fresh Cinnamon Powder.",
                price=9.89,
                category="Spices",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-3-min-300x300.jpg"
            ),
            Product(
                name="Granulated Garlic",
                description="Premium Granulated Garlic.",
                price=9.99,
                category="Spices",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-5-min-300x300.jpg"
            ),
            Product(
                name="Cayenne Red Pepper",
                description="Spicy Cayenne Red Pepper.",
                price=9.99,
                category="Chiles",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-6-min-300x300.jpg"
            ),
            Product(
                name="Ground Mexican Salt",
                description="Flavorful Ground Mexican Salt.",
                price=9.99,
                category="Sea Salts",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-8-min-300x300.jpg"
            ),
            Product(
                name="Ground Turmeric",
                description="Vibrant Ground Turmeric.",
                price=15.00,
                category="Turmeric",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-7-min-300x300.jpg"
            ),
            Product(
                name="Italian Herb Blend",
                description="Classic Italian Herb Blend.",
                price=40.00,
                category="Herbs",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-19-min-300x300.jpg"
            ),
            Product(
                name="Apple Pie Spice",
                description="Perfect spice for apple pies.",
                price=16.00,
                category="Spices",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-18-min-300x300.jpg"
            ),
            Product(
                name="Bloody Mary Mate",
                description="Spice up your Bloody Mary.",
                price=35.00,
                category="Spices",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-17-min-300x300.jpg"
            ),
            Product(
                name="Chile Rub",
                description="Rub for meats and grilling.",
                price=22.00,
                category="Chiles",
                image_url="https://xstore.b-cdn.net/elementor2/spices/wp-content/uploads/sites/10/2023/05/Product-image-16-min-300x300.jpg"
            ),
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        print(f"Database reset and seeded with {len(products)} products.")

if __name__ == '__main__':
    seed()
