from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Product, ProductPricing, Order, OrderItem, Category, HomeSection
import os
from werkzeug.utils import secure_filename
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.before_request
def restrict_access():
    if request.endpoint == 'admin.login':
        return

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))

    if getattr(current_user, 'role', 'customer') != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', 'customer') == 'admin':
            return redirect(url_for('admin.dashboard'))
        flash('You are already logged in as a customer.', 'info')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if user.role != 'admin':
                flash('Access denied. Not an admin account.', 'danger')
            else:
                login_user(user)
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/users')
@login_required
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@login_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def dashboard():
    products = Product.query.all()

    # Statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    total_users = User.query.count()
    total_products = Product.query.count()

    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status == 'Completed').scalar() or 0

    return render_template('admin/dashboard.html',
                           products=products,
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_users=total_users,
                           total_products=total_products,
                           total_revenue=total_revenue)

@admin_bp.route('/orders')
@login_required
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'Completed':
        order.status = 'Completed'
        db.session.commit()
        flash('Order confirmed successfully.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))

@admin_bp.route('/categories')
@login_required
def categories():
    categories = db.session.execute(db.select(Category)).scalars().all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        if Category.query.filter_by(name=name).first():
            flash('Category already exists', 'danger')
        else:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully', 'success')
            return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', title='Add Category')

@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        old_name = category.name
        new_name = request.form.get('name')

        if new_name != old_name:
            if Category.query.filter_by(name=new_name).first():
                flash('Category with this name already exists', 'danger')
                return render_template('admin/category_form.html', title='Edit Category', category=category)

            category.name = new_name
            # No need to manually update products as we use ForeignKey now
            db.session.commit()
            flash('Category updated successfully', 'success')
            return redirect(url_for('admin.categories'))
        else:
             return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', title='Edit Category', category=category)

@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    # Check if products exist in this category
    if Product.query.filter_by(category_id=category.id).first():
        flash('Cannot delete category with associated products. Please reassign products first.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = db.session.execute(db.select(Category)).scalars().all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        unit = request.form.get('unit', 'pcs')
        category_id = request.form.get('category')
        is_hidden = True if request.form.get('is_hidden') else False
        is_out_of_stock = True if request.form.get('is_out_of_stock') else False

        # Image handling
        image_url = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure static/images exists
                upload_dir = os.path.join('static', 'images')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                save_path = os.path.join(upload_dir, filename)
                # In a real app, use absolute path from app.config
                file.save(save_path)
                image_url = f'/static/images/{filename}'

        # Use a placeholder if no image
        if not image_url:
             image_url = 'https://via.placeholder.com/300'

        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            unit=unit,
            category_id=int(category_id),
            image_url=image_url,
            is_hidden=is_hidden,
            is_out_of_stock=is_out_of_stock
        )

        db.session.add(new_product)
        db.session.commit() # Commit to get ID

        # Handle Pricing
        quantities = request.form.getlist('pricing_quantity[]')
        prices = request.form.getlist('pricing_price[]')

        for q, p in zip(quantities, prices):
            if q and p:
                new_pricing = ProductPricing(
                    product_id=new_product.id,
                    quantity=float(q),
                    price=float(p)
                )
                db.session.add(new_pricing)

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_product.html', categories=categories)

@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = db.session.execute(db.select(Category)).scalars().all()

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.unit = request.form.get('unit', 'pcs')
        product.category_id = int(request.form.get('category'))
        product.is_hidden = True if request.form.get('is_hidden') else False
        product.is_out_of_stock = True if request.form.get('is_out_of_stock') else False

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join('static', 'images')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                save_path = os.path.join(upload_dir, filename)
                file.save(save_path)
                product.image_url = f'/static/images/{filename}'

        # Handle Pricing
        # Remove existing pricings
        ProductPricing.query.filter_by(product_id=product.id).delete()

        quantities = request.form.getlist('pricing_quantity[]')
        prices = request.form.getlist('pricing_price[]')

        for q, p in zip(quantities, prices):
            if q and p: # Ensure values exist
                new_pricing = ProductPricing(
                    product_id=product.id,
                    quantity=float(q),
                    price=float(p)
                )
                db.session.add(new_pricing)

        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_product.html', product=product, categories=categories)

@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/product/<int:product_id>/toggle_hidden', methods=['POST'])
@login_required
def toggle_hidden(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_hidden = not product.is_hidden
    db.session.commit()
    status = 'hidden' if product.is_hidden else 'visible'
    flash(f'Product {product.name} is now {status}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/product/<int:product_id>/toggle_stock', methods=['POST'])
@login_required
def toggle_stock(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_out_of_stock = not product.is_out_of_stock
    db.session.commit()
    status = 'out of stock' if product.is_out_of_stock else 'in stock'
    flash(f'Product {product.name} is now {status}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/settings/home', methods=['GET', 'POST'])
@login_required
def home_settings():
    section = HomeSection.query.filter_by(section_name='limited_offer').first()

    # Create default if missing (safety check)
    if not section:
        section = HomeSection(section_name='limited_offer')
        db.session.add(section)
        db.session.commit()

    if request.method == 'POST':
        section.title_fr = request.form.get('title_fr')
        section.title_ar = request.form.get('title_ar')
        section.title_en = request.form.get('title_en')
        section.text_fr = request.form.get('text_fr')
        section.text_ar = request.form.get('text_ar')
        section.text_en = request.form.get('text_en')

        # Date handling
        end_date_str = request.form.get('end_date')
        if end_date_str:
            try:
                section.end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass # Keep old date or handle error

        # Image handling
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join('static', 'images')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                save_path = os.path.join(upload_dir, filename)
                file.save(save_path)
                section.image_url = f'/static/images/{filename}'

        db.session.commit()
        flash('Home settings updated successfully', 'success')
        return redirect(url_for('admin.home_settings'))

    return render_template('admin/home_settings.html', section=section)
