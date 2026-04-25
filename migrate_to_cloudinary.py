import os
import io
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from flask import Flask
from models import db, Product, Category, HomeSection, DbImage

load_dotenv()

def migrate():
    # Setup a minimal Flask app for SQLAlchemy context
    app = Flask(__name__)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///luxfakia.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )

    with app.app_context():
        print("Starting image migration to Cloudinary...")

        def process_url(url, model_name, record_id):
            if not url or not url.startswith('/db_image/'):
                return url

            try:
                image_id = int(url.split('/')[-1])
                image_record = DbImage.query.get(image_id)
                
                if not image_record:
                    print(f"  Warning: No DbImage found for ID {image_id} (referenced by {model_name} {record_id})")
                    return url

                print(f"  Migrating image {image_id} for {model_name} {record_id} ({image_record.filename})...")
                
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    io.BytesIO(image_record.data),
                    folder="luxfakya",
                    public_id=f"migrated_{image_id}_{image_record.filename.rsplit('.', 1)[0]}",
                    overwrite=True
                )
                
                new_url = upload_result['secure_url']
                print(f"    Success! New URL: {new_url}")
                return new_url
            except Exception as e:
                print(f"  Error migrating image for {model_name} {record_id}: {e}")
                return url

        # Migrate Products
        products = Product.query.all()
        for p in products:
            new_url = process_url(p.image_url, "Product", p.id)
            if new_url != p.image_url:
                p.image_url = new_url

        # Migrate Categories
        categories = Category.query.all()
        for c in categories:
            new_url = process_url(c.image_url, "Category", c.id)
            if new_url != c.image_url:
                c.image_url = new_url

        # Migrate HomeSections
        sections = HomeSection.query.all()
        for s in sections:
            new_url = process_url(s.image_url, "HomeSection", s.id)
            if new_url != s.image_url:
                s.image_url = new_url

        db.session.commit()
        print("Migration completed!")

if __name__ == "__main__":
    migrate()
