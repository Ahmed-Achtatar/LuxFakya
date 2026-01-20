from app import create_app
from models import db, User

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

if __name__ == '__main__':
    seed()
