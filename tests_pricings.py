import unittest
from app import create_app, db
from models import User, Product, Category, ProductPricing

class PriceDisplayTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create Category
            c = Category(name='Dates')
            db.session.add(c)
            db.session.commit()

            # Create Product linked to Category
            # Base price is 100.0 (for 1kg usually)
            p = Product(name='TestProduct', price=100.0, category_id=c.id, image_url='', unit='Kg')
            db.session.add(p)
            db.session.commit()

            # Add pricings
            # 0.25kg -> 25.0
            pricing1 = ProductPricing(product_id=p.id, quantity=0.25, price=25.0, display_unit='g')
            # 1.0kg -> 100.0
            pricing2 = ProductPricing(product_id=p.id, quantity=1.0, price=100.0, display_unit='Kg')

            db.session.add(pricing1)
            db.session.add(pricing2)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_shop_price_display(self):
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # We expect to find '25.0 MAD' or similar if fixed.
        # Currently, it shows '100.0 MAD' (bug).
        # We search for the string inside the price element structure roughly
        # The template has: {{ product.price }} {{ get_text('currency') }}
        # Default currency is likely MAD or similar.

        # Normalize whitespace for easier checking
        content_normalized = ' '.join(content.split())

        # Let's check what is currently displayed.
        if '100.0 MAD' in content_normalized and '25.0 MAD' not in content_normalized:
            print("Reproduced: 100.0 MAD displayed (Base Price), 25.0 MAD missing.")
        elif '25.0 MAD' in content_normalized:
            print("Fixed: 25.0 MAD displayed.")
        else:
            print(f"Unknown state. Content snippet: {content_normalized[:1000]}")

        self.assertIn('25.0 MAD', content_normalized)
        # Note: 100.0 is present in the dropdown data-price="100.0", so we can't assertNotIn globally.
        # We should check if it's NOT in the price display area.
        # But '25.0 MAD' being present strongly suggests success if it wasn't there before.

    def test_index_price_display(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        content_normalized = ' '.join(content.split())

        self.assertIn('25.0 MAD', content_normalized)

if __name__ == '__main__':
    unittest.main()
