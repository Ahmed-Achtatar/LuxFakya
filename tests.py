import unittest
from app import create_app, db
from models import User, Product, Order, OrderItem, Category

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
            u = User(username='admin', role='admin')
            u.set_password('password')
            db.session.add(u)

            # Create Category
            c = Category(name='Dates')
            db.session.add(c)
            db.session.commit()

            # Create Product linked to Category
            p = Product(name='Test', price=10.0, category_id=c.id, image_url='', unit='kg')
            db.session.add(p)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LuxFakya', response.data)

    def test_favicon(self):
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/vnd.microsoft.icon')

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'healthy', 'message': 'Application is running'})

    def test_shop(self):
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        # Check if price is displayed without unit separator
        self.assertIn(b'10.0 MAD', response.data)
        self.assertNotIn(b'10.0 MAD / kg', response.data)

    def test_admin_access_denied(self):
        response = self.client.get('/admin/')
        # Should redirect to login (302) or show 401 depending on config. Flask-Login defaults to 401 or redirect.
        # My config sets login_view = 'admin_login' -> redirects.
        self.assertEqual(response.status_code, 302)

    def test_admin_login(self):
        response = self.client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tableau de bord', response.data)

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

    def test_checkout_flow(self):
        # Find the product id
        with self.app.app_context():
            p = Product.query.filter_by(name='Test').first()
            pid = p.id

        # 1. Add to cart
        self.client.post(f'/cart/add/{pid}', data={'quantity': 2.0})

        # 2. Checkout GET
        response = self.client.get('/checkout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Caisse', response.data)

        # 3. Checkout POST
        response = self.client.post('/checkout', data={'name': 'John Doe', 'phone': '123456789'})

        # Check redirect to order confirmation
        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            order = Order.query.first()
            self.assertIsNotNone(order)
            self.assertEqual(order.customer_name, 'John Doe')
            # 2 * 10.0 = 20.0. Less than 500, so +35 shipping = 55.0
            self.assertEqual(order.total_amount, 55.0)

            # Check Order Items
            items = OrderItem.query.filter_by(order_id=order.id).all()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].product_name, 'Test')
            self.assertEqual(items[0].quantity, 2.0)
            self.assertEqual(items[0].price_at_purchase, 10.0)

        # 4. Check Cart Cleared
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('cart'))

    def test_admin_orders(self):
        # Create an order
        with self.app.app_context():
            order = Order(customer_name='Jane Doe', total_amount=150.0)
            db.session.add(order)
            db.session.commit()
            order_id = order.id

        # Login admin
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'password'})

        # Check Orders Page
        response = self.client.get('/admin/orders')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)

        # Check Order Detail
        response = self.client.get(f'/admin/orders/{order_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)

    def test_homepage_structure(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for new elements
        self.assertIn(b'id="shop-filters"', response.data)
        self.assertIn(b'id="product-grid"', response.data)
        self.assertIn(b'id="show-more-btn"', response.data)
        # Check that filters are hidden initially
        self.assertIn(b'd-none mb-5', response.data)

if __name__ == '__main__':
    unittest.main()
