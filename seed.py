from app import create_app
from models import db, User, Product

app = create_app()

def seed():
    with app.app_context():
        db.create_all()

        # Check if admin exists
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('password123')
            db.session.add(user)
            print("Admin user created (admin/password123)")

        # Check if products exist
        if Product.query.count() == 0:
            products = [
                Product(name="Datte Majhoul Royal", description="Premium quality Majhoul dates from Morocco.", price=150.0, category="Dates", image_url="https://placehold.co/600x400/D4AF37/white?text=Majhoul+Royal"),
                Product(name="Datte Soukari", description="Sweet and soft Soukari dates.", price=90.0, category="Dates", image_url="https://placehold.co/600x400/D4AF37/white?text=Soukari"),
                Product(name="Amandes Grillées Salées", description="Crunchy roasted almonds with a touch of salt.", price=120.0, category="Nuts", image_url="https://placehold.co/600x400/D4AF37/white?text=Almonds"),
                Product(name="Noix de Cajou", description="Premium roasted cashew nuts.", price=140.0, category="Nuts", image_url="https://placehold.co/600x400/D4AF37/white?text=Cashews"),
                Product(name="Safran de Taliouine", description="Authentic Moroccan Saffron.", price=40.0, category="Spices", image_url="https://placehold.co/600x400/D4AF37/white?text=Saffron"),
                Product(name="Ras El Hanout", description="Traditional Moroccan spice blend.", price=60.0, category="Spices", image_url="https://placehold.co/600x400/D4AF37/white?text=Ras+El+Hanout"),
                Product(name="Abricots Secs", description="Dried apricots rich in flavor.", price=80.0, category="Dried Fruits", image_url="https://placehold.co/600x400/D4AF37/white?text=Apricots"),
                Product(name="Pack Prestige", description="A luxurious selection of dates and stuffed nuts.", price=450.0, category="Packs", image_url="https://placehold.co/600x400/D4AF37/white?text=Pack+Prestige"),
            ]

            db.session.bulk_save_objects(products)
            print(f"Added {len(products)} products.")
        else:
            print("Products already exist.")

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed()
