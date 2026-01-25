import unittest
from app import create_app, db
from models import User, Product, Category

class AdminFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            u = User(username='admin', role='admin')
            u.set_password('password')
            db.session.add(u)

            # Create Categories
            c1 = Category(name='Cat A')
            c2 = Category(name='Cat B')
            db.session.add(c1)
            db.session.add(c2)
            db.session.commit()

            # Create Products
            # Product A: Cat A, Price 10
            p1 = Product(name='Apple', price=10.0, category_id=c1.id, image_url='', unit='kg')
            # Product B: Cat B, Price 20
            p2 = Product(name='Banana', price=20.0, category_id=c2.id, image_url='', unit='kg')
            # Product C: Cat A, Price 5
            p3 = Product(name='Apricot', price=5.0, category_id=c1.id, image_url='', unit='kg')

            db.session.add_all([p1, p2, p3])
            db.session.commit()

            self.c1_id = c1.id
            self.c2_id = c2.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_admin(self):
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'password'})

    def test_dashboard_load(self):
        self.login_admin()
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Apple', response.data)
        self.assertIn(b'Banana', response.data)

    def test_search_filter(self):
        self.login_admin()
        # Search for "Apple"
        response = self.client.get('/admin/?search=Apple')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Apple', response.data)
        self.assertNotIn(b'Banana', response.data)

        # Search for "Apricot"
        response = self.client.get('/admin/?search=Apricot')
        self.assertIn(b'Apricot', response.data)
        self.assertNotIn(b'Apple', response.data)

    def test_category_filter(self):
        self.login_admin()
        # Filter by Cat A (Apple, Apricot)
        response = self.client.get(f'/admin/?category={self.c1_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Apple', response.data)
        self.assertIn(b'Apricot', response.data)
        self.assertNotIn(b'Banana', response.data)

        # Filter by Cat B (Banana)
        response = self.client.get(f'/admin/?category={self.c2_id}')
        self.assertIn(b'Banana', response.data)
        self.assertNotIn(b'Apple', response.data)

    def test_sort_name(self):
        self.login_admin()
        # Sort Name ASC (Apple, Apricot, Banana)
        response = self.client.get('/admin/?sort=name_asc')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        idx_apple = content.find('Apple')
        idx_banana = content.find('Banana')
        self.assertLess(idx_apple, idx_banana)

        # Sort Name DESC (Banana, Apricot, Apple)
        response = self.client.get('/admin/?sort=name_desc')
        content = response.data.decode('utf-8')
        idx_apple = content.find('Apple')
        idx_banana = content.find('Banana')
        self.assertGreater(idx_apple, idx_banana)

    def test_sort_price(self):
        self.login_admin()
        # Sort Price ASC (Apricot 5, Apple 10, Banana 20)
        response = self.client.get('/admin/?sort=price_asc')
        content = response.data.decode('utf-8')
        idx_apricot = content.find('Apricot')
        idx_banana = content.find('Banana')
        self.assertLess(idx_apricot, idx_banana)

        # Sort Price DESC (Banana 20, Apple 10, Apricot 5)
        response = self.client.get('/admin/?sort=price_desc')
        content = response.data.decode('utf-8')
        idx_apricot = content.find('Apricot')
        idx_banana = content.find('Banana')
        self.assertGreater(idx_apricot, idx_banana)

if __name__ == '__main__':
    unittest.main()
