from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

db = SQLAlchemy()

# Enable Foreign Keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer') # 'admin' or 'customer'

    # Profile Details
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)

    # Granular Permissions (For Moderators/Admins)
    can_manage_orders = db.Column(db.Boolean, default=False)
    can_manage_users = db.Column(db.Boolean, default=False)
    can_manage_products = db.Column(db.Boolean, default=False)
    can_manage_content = db.Column(db.Boolean, default=False)

    # Detailed Permissions
    can_add_product = db.Column(db.Boolean, default=False)
    can_edit_product = db.Column(db.Boolean, default=False)
    can_delete_product = db.Column(db.Boolean, default=False)

    can_add_category = db.Column(db.Boolean, default=False)
    can_edit_category = db.Column(db.Boolean, default=False)
    can_delete_category = db.Column(db.Boolean, default=False)

    can_add_user = db.Column(db.Boolean, default=False)
    can_edit_user = db.Column(db.Boolean, default=False)
    can_delete_user = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', backref='user', lazy=True)

    @property
    def is_staff(self):
        return bool((self.role == 'admin') or \
               self.can_manage_orders or \
               self.can_manage_users or \
               self.can_manage_products or \
               self.can_manage_content or \
               self.can_add_product or \
               self.can_edit_product or \
               self.can_delete_product or \
               self.can_add_category or \
               self.can_edit_category or \
               self.can_delete_category or \
               self.can_add_user or \
               self.can_edit_user or \
               self.can_delete_user)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))

class DbImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=True)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url
        }

class ProductPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    display_unit = db.Column(db.String(20), default='Kg')

    def to_dict(self):
        return {
            'quantity': self.quantity,
            'price': self.price,
            'display_unit': self.display_unit
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False, default='pcs')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

    image_url = db.Column(db.String(500), nullable=True)
    is_hidden = db.Column(db.Boolean, default=False)
    is_out_of_stock = db.Column(db.Boolean, default=False)
    pricings = db.relationship('ProductPricing', backref='product', cascade="all, delete-orphan", lazy=True, order_by='ProductPricing.quantity')

    @property
    def display_image_url(self):
        if self.image_url:
            return self.image_url
        if self.category:
            if 'Dattes' in self.category.name:
                return '/static/images/dates.png'
            if 'Fruits secs' in self.category.name:
                return '/static/images/nuts.png'
            if 'Fruits confits' in self.category.name or 'Fruits lyophilisés' in self.category.name:
                return '/static/images/driedfood.png'
            if 'Offres' in self.category.name:
                return '/static/images/gift.png'
        return '/static/images/logo.png'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'unit': self.unit,
            'category': self.category.name if self.category else None,
            'image_url': self.image_url,
            'is_hidden': self.is_hidden,
            'is_out_of_stock': self.is_out_of_stock,
            'pricings': [p.to_dict() for p in self.pricings]
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    customer_name = db.Column(db.String(150), nullable=False)
    customer_email = db.Column(db.String(150), nullable=True)
    customer_phone = db.Column(db.String(50), nullable=True)
    customer_address = db.Column(db.String(255), nullable=True)
    customer_city = db.Column(db.String(100), nullable=True)

    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='SET NULL'), nullable=True)

    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

class HomeSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'limited_offer'

    # Content stored for multiple languages
    title_fr = db.Column(db.String(150), nullable=True)
    title_ar = db.Column(db.String(150), nullable=True)
    title_en = db.Column(db.String(150), nullable=True)

    text_fr = db.Column(db.Text, nullable=True)
    text_ar = db.Column(db.Text, nullable=True)
    text_en = db.Column(db.Text, nullable=True)

    image_url = db.Column(db.String(500), nullable=True)
    end_date = db.Column(db.DateTime, nullable=True) # For countdown
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'section_name': self.section_name,
            'title_fr': self.title_fr,
            'title_ar': self.title_ar,
            'title_en': self.title_en,
            'text_fr': self.text_fr,
            'text_ar': self.text_ar,
            'text_en': self.text_en,
            'image_url': self.image_url,
            'end_date': self.end_date,
            'is_active': self.is_active
        }

class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }
