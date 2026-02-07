from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Product, ProductPricing, Order, OrderItem, Category, HomeSection, DbImage, UserLog
import os
import uuid
import io
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_and_save_image(file):
    filename = secure_filename(file.filename)
    filename_base = filename.rsplit('.', 1)[0]

    try:
        img = Image.open(file)
        max_width = 1024
        if img.width > max_width:
             ratio = max_width / float(img.width)
             new_height = int(float(img.height) * ratio)
             img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save to buffer
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='WEBP', optimize=True, quality=80)
        output_buffer.seek(0)

        new_image = DbImage(
            filename=f"{filename_base}.webp",
            data=output_buffer.getvalue(),
            mimetype='image/webp'
        )
        db.session.add(new_image)
        db.session.commit()

        return url_for('main.get_db_image', image_id=new_image.id)

    except Exception as e:
        current_app.logger.error(f"Optimization error: {e}")
        # Fallback to original format
        file.seek(0)
        data = file.read()

        new_image = DbImage(
            filename=filename,
            data=data,
            mimetype=getattr(file, 'content_type', 'application/octet-stream')
        )
        db.session.add(new_image)
        db.session.commit()

        return url_for('main.get_db_image', image_id=new_image.id)

@admin_bp.before_request
def restrict_access():
    if request.endpoint == 'admin.login':
        return

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))

    # Allow access if admin or has any management permission
    is_admin = getattr(current_user, 'role', 'customer') == 'admin'
    has_perms = (
        current_user.can_manage_orders or
        current_user.can_manage_users or
        current_user.can_manage_products or
        current_user.can_manage_content
    )

    if not (is_admin or has_perms):
        flash('Access denied. Admin or Moderator privileges required.', 'danger')
        return redirect(url_for('main.index'))

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if getattr(current_user, 'role', 'customer') == 'admin':
                return f(*args, **kwargs)

            if getattr(current_user, permission_name, False):
                return f(*args, **kwargs)

            flash('Access denied. Insufficient permissions.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return decorated_function
    return decorator

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
@permission_required('can_manage_users')
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    staff_users = [u for u in users if u.is_staff]
    client_users = [u for u in users if not u.is_staff]
    return render_template('admin/users.html', staff_users=staff_users, client_users=client_users)

@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@permission_required('can_manage_users')
def user_detail(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Only allow changing permissions if current user is admin
        if getattr(current_user, 'role', 'customer') == 'admin':
             if request.form.get('action') == 'promote':
                 user.can_manage_orders = True # Default permission to make them staff
                 db.session.commit()
                 flash('User promoted to Moderator. You can now assign specific permissions.', 'success')
                 return redirect(url_for('admin.user_detail', user_id=user.id))

             user.can_manage_orders = True if request.form.get('can_manage_orders') else False
             user.can_manage_users = True if request.form.get('can_manage_users') else False
             user.can_manage_products = True if request.form.get('can_manage_products') else False
             user.can_manage_content = True if request.form.get('can_manage_content') else False
             db.session.commit()
             flash('Permissions updated.', 'success')
        else:
             flash('Only Admins can change permissions.', 'warning')

    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def dashboard():
    # Filter Parameters
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category')
    sort_by = request.args.get('sort', 'newest')

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if category_id and category_id.isdigit():
         query = query.filter(Product.category_id == int(category_id))

    # Sorting
    if sort_by == 'name_asc':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Product.name.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else: # newest or default
        query = query.order_by(Product.id.desc())

    products = query.all()
    categories = Category.query.all()

    # Statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    total_users = User.query.count()
    total_products = Product.query.count()

    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status == 'Completed').scalar() or 0

    return render_template('admin/dashboard.html',
                           products=products,
                           categories=categories,
                           search=search,
                           category_id=category_id,
                           sort_by=sort_by,
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_users=total_users,
                           total_products=total_products,
                           total_revenue=total_revenue)

@admin_bp.route('/logs')
@login_required
@permission_required('can_manage_users')
def logs():
    logs = UserLog.query.order_by(UserLog.timestamp.desc()).limit(100).all()
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/orders')
@login_required
@permission_required('can_manage_orders')
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/<int:order_id>')
@login_required
@permission_required('can_manage_orders')
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
@login_required
@permission_required('can_manage_orders')
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'Completed':
        order.status = 'Completed'
        db.session.commit()
        flash('Order confirmed successfully.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))

@admin_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
@permission_required('can_manage_orders')
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        db.session.commit()
        flash('Order cancelled successfully.', 'warning')
    return redirect(url_for('admin.order_detail', order_id=order.id))

@admin_bp.route('/categories')
@login_required
@permission_required('can_manage_products')
def categories():
    categories = db.session.execute(db.select(Category)).scalars().all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@permission_required('can_manage_products')
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        image_url = None

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                image_url = optimize_and_save_image(file)

        if Category.query.filter_by(name=name).first():
            flash('Category already exists', 'danger')
        else:
            category = Category(name=name, image_url=image_url)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully', 'success')
            return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', title='Add Category')

@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('can_manage_products')
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        new_name = request.form.get('name')

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                category.image_url = optimize_and_save_image(file)

        if new_name != category.name:
            if Category.query.filter_by(name=new_name).first():
                flash('Category with this name already exists', 'danger')
                return render_template('admin/category_form.html', title='Edit Category', category=category)
            category.name = new_name

        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', title='Edit Category', category=category)

@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('can_manage_products')
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
@permission_required('can_manage_products')
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
                image_url = optimize_and_save_image(file)

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
        units = request.form.getlist('pricing_unit[]')

        # Ensure we have a unit list matching others
        if len(units) < len(quantities):
             units.extend(['Kg'] * (len(quantities) - len(units)))

        for q, p, u in zip(quantities, prices, units):
            if q and p:
                qty_val = float(q)
                unit_val = u if u else 'Kg'

                # Normalize quantity if unit is grams
                if unit_val == 'g':
                    qty_val = qty_val / 1000.0

                new_pricing = ProductPricing(
                    product_id=new_product.id,
                    quantity=qty_val,
                    price=float(p),
                    display_unit=unit_val
                )
                db.session.add(new_pricing)

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_product.html', categories=categories)

@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@permission_required('can_manage_products')
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
                product.image_url = optimize_and_save_image(file)

        # Handle Pricing
        # Remove existing pricings
        ProductPricing.query.filter_by(product_id=product.id).delete()

        quantities = request.form.getlist('pricing_quantity[]')
        prices = request.form.getlist('pricing_price[]')
        units = request.form.getlist('pricing_unit[]')

        # Fallback for units length safety
        if len(units) < len(quantities):
             units.extend(['Kg'] * (len(quantities) - len(units)))

        for q, p, u in zip(quantities, prices, units):
            if q and p: # Ensure values exist
                qty_val = float(q)
                unit_val = u if u else 'Kg'

                # Normalize quantity if unit is grams
                if unit_val == 'g':
                    qty_val = qty_val / 1000.0

                new_pricing = ProductPricing(
                    product_id=product.id,
                    quantity=qty_val,
                    price=float(p),
                    display_unit=unit_val
                )
                db.session.add(new_pricing)

        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_product.html', product=product, categories=categories)

@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@permission_required('can_manage_products')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/product/<int:product_id>/toggle_hidden', methods=['POST'])
@login_required
@permission_required('can_manage_products')
def toggle_hidden(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_hidden = not product.is_hidden
    db.session.commit()
    status = 'hidden' if product.is_hidden else 'visible'
    flash(f'Product {product.name} is now {status}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/product/<int:product_id>/toggle_stock', methods=['POST'])
@login_required
@permission_required('can_manage_products')
def toggle_stock(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_out_of_stock = not product.is_out_of_stock
    db.session.commit()
    status = 'out of stock' if product.is_out_of_stock else 'in stock'
    flash(f'Product {product.name} is now {status}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/settings/home', methods=['GET', 'POST'])
@login_required
@permission_required('can_manage_content')
def home_settings():
    # Define managed sections
    target_sections = ['hero_slide_1', 'hero_slide_2', 'hero_slide_3', 'limited_offer']
    sections = {}

    # Fetch or Create
    for name in target_sections:
        s = HomeSection.query.filter_by(section_name=name).first()
        if not s:
            s = HomeSection(section_name=name)
            db.session.add(s)
        sections[name] = s

    # Commit any new sections
    if db.session.dirty or db.session.new:
        db.session.commit()

    if request.method == 'POST':
        section_name = request.form.get('section_name')
        if section_name and section_name in sections:
            section = sections[section_name]

            section.title_fr = request.form.get(f'title_fr_{section_name}')
            section.title_ar = request.form.get(f'title_ar_{section_name}')
            section.title_en = request.form.get(f'title_en_{section_name}')

            section.text_fr = request.form.get(f'text_fr_{section_name}')
            section.text_ar = request.form.get(f'text_ar_{section_name}')
            section.text_en = request.form.get(f'text_en_{section_name}')

            # Date handling (only for limited_offer really, but generic is fine)
            end_date_str = request.form.get(f'end_date_{section_name}')
            if end_date_str:
                try:
                    section.end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass

            # Active toggle
            section.is_active = True if request.form.get(f'is_active_{section_name}') else False

            # Image handling
            file_key = f'image_{section_name}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and allowed_file(file.filename):
                    section.image_url = optimize_and_save_image(file)

            db.session.commit()
            flash(f'Section {section_name} updated successfully', 'success')
            return redirect(url_for('admin.home_settings'))

    return render_template('admin/home_settings.html', sections=sections)
