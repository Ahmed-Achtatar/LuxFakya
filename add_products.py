from app import create_app
from models import db, Product, ProductPricing, Category

app = create_app()

products_data = [
    {"ar": "أكاجو مكلي", "en": "Cashew (Normal)", "prices": {1.0: 145.00, 0.75: 110.00, 0.5: 75.00, 0.25: 40.00}},
    {"ar": "أكاجو روايال", "en": "Cashew (Royal)", "prices": {1.0: 180.00, 0.75: 135.00, 0.5: 90.00, 0.25: 50.00}},
    {"ar": "بيسطاش", "en": "Pistachio", "prices": {1.0: 150.00, 0.75: 110.00, 0.5: 75.00, 0.25: 40.00}},
    {"ar": "كركاع", "en": "Walnut", "prices": {1.0: 95.00, 0.75: 75.00, 0.5: 50.00, 0.25: 25.00}},
    {"ar": "لوز مكلي بالملحة", "en": "Almond (Royal)", "prices": {1.0: 130.00, 0.75: 97.00, 0.5: 65.00, 0.25: 35.00}},
    {"ar": "كوكو مكلي", "en": "Peanuts (Salted)", "prices": {1.0: 45.00, 0.75: 35.00, 0.5: 25.00, 0.25: 12.00}},
    {"ar": "كوكو فرماج حمـر", "en": "Peanuts (Red Cheese)", "prices": {1.0: 60.00, 0.75: 45.00, 0.5: 30.00, 0.25: 18.00}},
    {"ar": "كوكو فرماج أبيض", "en": "Peanuts (White Cheese)", "prices": {1.0: 60.00, 0.75: 45.00, 0.5: 30.00, 0.25: 18.00}},
    {"ar": "كوكو فرماج حار", "en": "Peanuts (Spicy Cheese)", "prices": {1.0: 60.00, 0.75: 45.00, 0.5: 30.00, 0.25: 18.00}},
    {"ar": "زبيب", "en": "Raisins", "prices": {1.0: 70.00, 0.75: 50.00, 0.5: 35.00, 0.25: 17.50}},
    {"ar": "حمص تركيا", "en": "Chickpeas (Turkey)", "prices": {1.0: 70.00, 0.75: 50.00, 0.5: 35.00, 0.25: 17.50}},
    {"ar": "ذرة", "en": "Corn (Toasted)", "prices": {1.0: 80.00, 0.75: 60.00, 0.5: 40.00, 0.25: 20.00}},
    {"ar": "جوز برازيل", "en": "Brazil Nuts", "prices": {1.0: 330.00, 0.75: 260.00, 0.5: 175.00, 0.25: 85.00}},
    {"ar": "كوكو زرارع", "en": "Peanuts (Seeded/Sesame)", "prices": {1.0: 80.00, 0.75: 60.00, 0.5: 40.00, 0.25: 20.00}},
    {"ar": "لوز بالنافع", "en": "Almonds (Salted)", "prices": {1.0: 130.00, 0.75: 97.00, 0.5: 65.00, 0.25: 35.00}},
    {"ar": "بيكان", "en": "Pecan", "prices": {1.0: 240.00, 0.75: 185.00, 0.5: 125.00, 0.25: 65.00}},
]

def add_products():
    with app.app_context():
        category_name = 'Fruits secs / fruits à coque (مكسرات / فاكية)'
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            print(f"Category '{category_name}' not found!")
            return

        for item in products_data:
            name = f"{item['en']} ({item['ar']})"
            existing_product = Product.query.filter_by(name=name).first()

            if existing_product:
                print(f"Product '{name}' already exists. Updating prices...")
                product = existing_product
                product.price = item['prices'][1.0]
                product.category_id = category.id
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
