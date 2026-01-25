from app import create_app
from models import db, Product, ProductPricing, Category

app = create_app()

products_data = [
    {"ar": "أكاجو مكلي", "fr": "Noix de Cajou Grillées", "prices": {1.0: 145.00, 0.75: 110.00, 0.5: 75.00, 0.25: 40.00}},
    {"ar": "أكاجو روايال", "fr": "Noix de Cajou Royales", "prices": {1.0: 180.00, 0.75: 135.00, 0.5: 90.00, 0.25: 50.00}},
    {"ar": "بيسطاش", "fr": "Pistaches", "prices": {1.0: 150.00, 0.75: 110.00, 0.5: 75.00, 0.25: 40.00}},
    {"ar": "كركاع", "fr": "Noix", "prices": {1.0: 95.00, 0.75: 75.00, 0.5: 50.00, 0.25: 25.00}},
    {"ar": "لوز مكلي بالملحة", "fr": "Amandes Grillées Salées", "prices": {1.0: 130.00, 0.75: 97.00, 0.5: 65.00, 0.25: 35.00}},
    {"ar": "كوكو مكلي", "fr": "Cacahuètes Salées", "prices": {1.0: 45.00, 0.75: 35.00, 0.5: 25.00, 0.25: 12.00}},
    {"ar": "كوكو فرماج حمـر", "fr": "Cacahuètes au Fromage Rouge", "prices": {1.0: 60.00, 0.75: 45.00, 0.5: 30.00, 0.25: 18.00}},
    {"ar": "كوكو فرماج أبيض", "fr": "Cacahuètes au Fromage Blanc", "prices": {1.0: 60.00, 0.75: 45.00, 0.5: 30.00, 0.25: 18.00}},
    {"ar": "كوكو فرماج حار", "fr": "Cacahuètes au Fromage Piquant", "prices": {1.0: 60.00, 0.75: 45.00, 0.5: 30.00, 0.25: 18.00}},
    {"ar": "زبيب", "fr": "Raisins Secs", "prices": {1.0: 70.00, 0.75: 50.00, 0.5: 35.00, 0.25: 17.50}},
    {"ar": "حمص تركيا", "fr": "Pois Chiches (Turquie)", "prices": {1.0: 70.00, 0.75: 50.00, 0.5: 35.00, 0.25: 17.50}},
    {"ar": "ذرة", "fr": "Maïs Grillé", "prices": {1.0: 80.00, 0.75: 60.00, 0.5: 40.00, 0.25: 20.00}},
    {"ar": "جوز برازيل", "fr": "Noix du Brésil", "prices": {1.0: 330.00, 0.75: 260.00, 0.5: 175.00, 0.25: 85.00}},
    {"ar": "كوكو زرارع", "fr": "Cacahuètes aux Graines", "prices": {1.0: 80.00, 0.75: 60.00, 0.5: 40.00, 0.25: 20.00}},
    {"ar": "لوز بالنافع", "fr": "Amandes à l'Anis", "prices": {1.0: 130.00, 0.75: 97.00, 0.5: 65.00, 0.25: 35.00}},
    {"ar": "بيكان", "fr": "Noix de Pécan", "prices": {1.0: 240.00, 0.75: 185.00, 0.5: 125.00, 0.25: 65.00}},
]

def add_products():
    with app.app_context():
        category_name = 'Fruits secs / fruits à coque (مكسرات / فاكية)'
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            print(f"Category '{category_name}' not found!")
            return

        for item in products_data:
            name = f"{item['fr']} ({item['ar']})"

            # Find existing product by Arabic name to update it (renaming from English to French)
            # We look for any product whose name contains the Arabic string
            products = Product.query.filter(Product.name.like(f"%({item['ar']})")).all()

            product = None
            if products:
                # We assume the first match is the one we want to update/rename
                product = products[0]
                print(f"Found existing product matching '{item['ar']}': {product.name}")
                if product.name != name:
                    print(f"Renaming to: {name}")
                    product.name = name
                product.price = item['prices'][1.0]
                product.category_id = category.id
            else:
                # Also check exact match just in case
                existing_product = Product.query.filter_by(name=name).first()
                if existing_product:
                    product = existing_product
                    print(f"Product '{name}' already exists. Updating...")
                else:
                    print(f"Creating product '{name}'...")
                    product = Product(
                        name=name,
                        price=item['prices'][1.0],
                        unit='Kg',
                        category_id=category.id,
                        is_hidden=False,
                        is_out_of_stock=False
                    )
                    db.session.add(product)
                    db.session.flush()

            # Remove existing pricings
            ProductPricing.query.filter_by(product_id=product.id).delete()

            # Add new pricings
            for qty, price in item['prices'].items():
                pricing = ProductPricing(
                    product_id=product.id,
                    quantity=qty,
                    price=price
                )
                db.session.add(pricing)

        db.session.commit()
        print("Products added/updated successfully.")

if __name__ == "__main__":
    add_products()
