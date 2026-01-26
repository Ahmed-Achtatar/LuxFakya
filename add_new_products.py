from app import create_app
from models import db, Product, ProductPricing, Category

app = create_app()

products_list = [
    # Item (Arabic), French Name, Category, Prices {1.0, 0.75, 0.5, 0.25}
    {
        "ar": "فانيد",
        "fr": "Fanid",
        "category": "Fruits confits (فواكه معسلة)", # Best fit for candy
        "prices": {1.0: 60, 0.75: 45, 0.5: 30, 0.25: 15}
    },
    {
        "ar": "شريحة",
        "fr": "Figues Sèches",
        "category": "Fruits secs / fruits à coque (مكسرات / فاكية)",
        "prices": {1.0: 120.0, 0.75: 95.0, 0.5: 62.0, 0.25: 33.0}
    },
    {
        "ar": "ت. سكري",
        "fr": "Dattes Sukari",
        "category": "Dattes (تمور)",
        "prices": {1.0: 40, 0.75: 30, 0.5: 20, 0.25: 10}
    },
    {
        "ar": "مجهول",
        "fr": "Dattes Majhoul",
        "category": "Dattes (تمور)",
        "prices": {1.0: 120, 0.75: 95, 0.5: 63, 0.25: 32}
    },
    {
        "ar": "عرش تونس",
        "fr": "Dattes Branchées Tunisie",
        "category": "Dattes (تمور)",
        "prices": {1.0: 45, 0.75: 35, 0.5: 25, 0.25: 15.0}
    },
    {
        "ar": "عرش جزائر",
        "fr": "Dattes Branchées Algérie",
        "category": "Dattes (تمور)",
        "prices": {1.0: 60.0, 0.75: 50.0, 0.5: 33.0, 0.25: 16.0}
    },
    {
        "ar": "بلاد",
        "fr": "Dattes Belad",
        "category": "Dattes (تمور)",
        "prices": {1.0: 60, 0.75: 50, 0.5: 33, 0.25: 16}
    },
    # Candied Fruits
    {
        "ar": "كيوي معسل",
        "fr": "Kiwi Confit",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
    {
        "ar": "أناناس",
        "fr": "Ananas Confit",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
    {
        "ar": "مونݣ",
        "fr": "Mangue Confite",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
    {
        "ar": "تفاح",
        "fr": "Pomme Confite",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
    {
        "ar": "ليمون",
        "fr": "Citron Confit",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
    {
        "ar": "فريز",
        "fr": "Fraise Confite",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 140, 0.75: 105, 0.5: 70, 0.25: 38}
    },
    {
        "ar": "بالموس",
        "fr": "Pamplemousse Confit",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
    {
        "ar": "بنان",
        "fr": "Banane Confite",
        "category": "Fruits confits (فواكه معسلة)",
        "prices": {1.0: 120, 0.75: 90, 0.5: 60, 0.25: 32}
    },
]

def add_new_products():
    with app.app_context():
        # Pre-fetch categories
        categories = {}
        for item in products_list:
            cat_name = item['category']
            if cat_name not in categories:
                cat = Category.query.filter_by(name=cat_name).first()
                if not cat:
                    print(f"Warning: Category '{cat_name}' not found! Skipping products for this category.")
                    categories[cat_name] = None
                else:
                    categories[cat_name] = cat

        for item in products_list:
            category = categories.get(item['category'])
            if not category:
                continue

            name = f"{item['fr']} ({item['ar']})"

            # Check existing
            product = None
            # Search by Arabic name part to find matches even if French name differs
            products = Product.query.filter(Product.name.like(f"%({item['ar']})")).all()
            if products:
                product = products[0]
                print(f"Updating existing product: {product.name} -> {name}")
                if product.name != name:
                    product.name = name
                product.category_id = category.id
                product.price = item['prices'][1.0] # Update base price
            else:
                # Check exact name match
                existing = Product.query.filter_by(name=name).first()
                if existing:
                    product = existing
                    print(f"Updating existing product (exact match): {name}")
                    product.category_id = category.id
                    product.price = item['prices'][1.0]
                else:
                    print(f"Creating new product: {name}")
                    product = Product(
                        name=name,
                        price=item['prices'][1.0],
                        unit='Kg',
                        category_id=category.id,
                        is_hidden=False,
                        is_out_of_stock=False
                    )
                    db.session.add(product)
                    db.session.flush() # get ID

            # Update pricings
            # Delete old pricings
            ProductPricing.query.filter_by(product_id=product.id).delete()

            # Add new pricings
            for qty, price in item['prices'].items():
                # Determine display unit based on product unit
                p_unit = product.unit if product.unit else 'Kg'
                display_unit = p_unit
                if p_unit.lower() == 'kg':
                    display_unit = 'g' if qty < 1.0 else 'Kg'

                pricing = ProductPricing(
                    product_id=product.id,
                    quantity=qty,
                    price=price,
                    display_unit=display_unit
                )
                db.session.add(pricing)

        db.session.commit()
        print("All products processed.")

if __name__ == "__main__":
    add_new_products()
