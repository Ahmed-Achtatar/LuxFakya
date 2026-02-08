import unittest
from app import create_app, db
from models import User

class AdminModeratorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create admin
            self.admin = User(username='admin', email='admin@example.com', role='admin')
            self.admin.set_password('password')
            db.session.add(self.admin)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.client.post('/admin/login', data={'username': username, 'password': password}, follow_redirects=True)

    def test_add_moderator(self):
        self.login('admin', 'password')

        # Test adding a moderator
        response = self.client.post('/admin/users/add', data={
            'username': 'new_mod',
            'email': 'mod@test.com',
            'password': 'modpassword',
            'can_manage_orders': 'on'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # Expect localized message (French default)
        self.assertIn('Utilisateur créé avec succès'.encode('utf-8'), response.data)

        with self.app.app_context():
            user = User.query.filter_by(username='new_mod').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.can_manage_orders)
            self.assertFalse(user.can_manage_users)
            self.assertFalse(user.can_manage_products)
            self.assertFalse(user.can_manage_content)

    def test_moderator_redirect_and_sidebar(self):
        # Create a restricted moderator
        with self.app.app_context():
            mod = User(username='order_mod', email='order@test.com', role='customer', can_manage_orders=True)
            mod.set_password('password')
            db.session.add(mod)
            db.session.commit()

        self.login('order_mod', 'password')

        # Test Dashboard Redirect
        response = self.client.get('/admin/', follow_redirects=True)
        # Should be redirected to /admin/orders. The response is the final page content.
        # Check if we landed on orders page.
        # "Orders" usually appears in title or content.
        # Note: App defaults to French in tests, so looking for "Commandes"
        self.assertIn(b'Commandes', response.data)

        content = response.data.decode('utf-8')
        # "Categories" link should NOT be present
        self.assertNotIn('href="/admin/categories"', content)
        # "Users" link should NOT be present
        self.assertNotIn('href="/admin/users"', content)
        # "Settings" link should NOT be present
        self.assertNotIn('href="/admin/settings/home"', content)

        # "Orders" link should be present
        self.assertIn('href="/admin/orders"', content)

if __name__ == '__main__':
    unittest.main()
