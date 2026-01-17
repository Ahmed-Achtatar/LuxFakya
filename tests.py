import unittest
from app import create_app, db
from models import User, Product

class LuxFakiaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            u = User(username='admin')
            u.set_password('password')
            db.session.add(u)
            p = Product(name='Test', price=10.0, category='Dates', image_url='', unit='kg')
            db.session.add(p)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LuxFakia', response.data)

    def test_shop(self):
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        # Check if unit is displayed
        self.assertIn(b'/ kg', response.data)

    def test_admin_access_denied(self):
        response = self.client.get('/admin/')
        # Should redirect to login (302) or show 401 depending on config. Flask-Login defaults to 401 or redirect.
        # My config sets login_view = 'admin_login' -> redirects.
        self.assertEqual(response.status_code, 302)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_add_to_cart_quantity(self):
        # Find the product id
        with self.app.app_context():
            p = Product.query.filter_by(name='Test').first()
            pid = p.id

        # Test adding with default quantity (GET)
        response = self.client.get(f'/cart/add/{pid}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as sess:
            cart = sess['cart']
            self.assertIn(str(pid), cart)
            self.assertEqual(cart[str(pid)], 1.0)

        # Clear cart
        with self.client.session_transaction() as sess:
            sess['cart'] = {}

        # Test adding with custom quantity via POST
        response = self.client.post(f'/cart/add/{pid}', data={'quantity': 3}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as sess:
            cart = sess['cart']
            self.assertIn(str(pid), cart)
            self.assertEqual(cart[str(pid)], 3.0)

    def test_add_to_cart_float_quantity(self):
        # Find the product id
        with self.app.app_context():
            p = Product.query.filter_by(name='Test').first()
            pid = p.id

        # Test adding with float quantity via POST
        response = self.client.post(f'/cart/add/{pid}', data={'quantity': 1.5}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as sess:
            cart = sess['cart']
            self.assertIn(str(pid), cart)
            self.assertEqual(cart[str(pid)], 1.5)

if __name__ == '__main__':
    unittest.main()
