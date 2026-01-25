from app import create_app
from models import db, User, Category

app = create_app()

def seed():
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Check if Admin user exists
        admin = User.query.filter_by(username='admin').first()

        if not admin:
            print("Creating default admin user...")
            admin = User(username='admin', email='admin@luxfakia.com', role='admin')
            admin.set_password('password123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
            print("Username: admin")
            print("Password: password123")
        else:
            print("Admin user already exists. Skipping creation.")

        # Seed Categories
        default_categories = [
            'Offres (عروض)',
            'Dattes (تمور)',
            'Fruits secs / fruits à coque (مكسرات / فاكية)',
            'Fruits confits (فواكه معسلة)',
            'Fruits lyophilisés (فواكه مجففة بالتبريد)'
        ]

        print("Seeding categories...")

        # Add new categories
        for cat_name in default_categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                print(f"Creating category: {cat_name}")
                category = Category(name=cat_name)
                db.session.add(category)
            else:
                print(f"Category exists: {cat_name}")

        # Remove old categories
        existing_categories = Category.query.all()
        for cat in existing_categories:
            if cat.name not in default_categories:
                print(f"Deleting old category: {cat.name}")
                db.session.delete(cat)

        db.session.commit()
        print("Seeding complete.")

if __name__ == '__main__':
    seed()
