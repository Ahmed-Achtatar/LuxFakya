import unittest
from app import create_app, db
from models import User

class AdminUserManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create users
            self.admin = User(username='admin', email='admin@example.com', role='admin')
            self.admin.set_password('password')
            db.session.add(self.admin)

            self.mod = User(username='mod', email='mod@example.com', role='customer', can_manage_orders=True)
            self.mod.set_password('password')
            db.session.add(self.mod)

            self.client_user = User(username='client', email='client@example.com', role='customer', can_manage_orders=False)
            self.client_user.set_password('password')
            db.session.add(self.client_user)

            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_admin(self):
        return self.client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)

    def test_users_list_separation(self):
        self.login_admin()
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for sections
        self.assertIn('Staff (Admin & Moderators)', content)
        self.assertIn('Clients', content)

        # Check that 'mod' is in Staff section (rudimentary check based on order or proximity,
        # but simply checking presence is a good start.
        # Better: check if "Moderator" badge is near "mod")

        # Verify "mod" appears
        self.assertIn('mod', content)
        # Verify "client" appears
        self.assertIn('client', content)

        # We can check specific badges
        # 'mod' should have 'Moderator' badge
        # 'client' should have 'Customer' badge

    def test_promote_client(self):
        self.login_admin()

        # Get client ID
        with self.app.app_context():
            client_id = User.query.filter_by(username='client').first().id

        # Visit user detail page
        response = self.client.get(f'/admin/users/{client_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Promote to Moderator', response.data.decode('utf-8'))
        self.assertNotIn('Can Manage Orders', response.data.decode('utf-8')) # Form should be hidden

        # Promote
        response = self.client.post(f'/admin/users/{client_id}', data={'action': 'promote'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('User promoted to Moderator', response.data.decode('utf-8'))

        # Check permissions form is now visible
        self.assertIn('Can Manage Orders', response.data.decode('utf-8'))

        # Check DB
        with self.app.app_context():
            u = User.query.get(client_id)
            self.assertTrue(u.is_staff)
            self.assertTrue(u.can_manage_orders)

if __name__ == '__main__':
    unittest.main()
