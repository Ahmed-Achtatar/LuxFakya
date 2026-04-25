import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

images_to_migrate = [
    'logo.png',
    'dates.png',
    'nuts.png',
    'driedfood.png',
    'gift.png',
    'slide1.png',
    'slide2.png',
    'slide3.png'
]

static_images_path = 'static/images'

results = {}

print("Migrating static assets to Cloudinary...")

for img in images_to_migrate:
    file_path = os.path.join(static_images_path, img)
    if os.path.exists(file_path):
        print(f"Uploading {img} ({os.path.getsize(file_path)/1024/1024:.2f} MB)...")
        try:
            upload_result = cloudinary.uploader.upload(
                file_path,
                folder="luxfakya/static",
                public_id=img.split('.')[0],
                overwrite=True,
                resource_type="image"
            )
            results[img] = upload_result['secure_url']
            print(f"  Success: {results[img]}")
        except Exception as e:
            print(f"  Error uploading {img}: {e}")
    else:
        print(f"  File not found: {file_path}")

print("\nMigration Results (Copy these URLs!):")
for img, url in results.items():
    print(f"{img}: {url}")
