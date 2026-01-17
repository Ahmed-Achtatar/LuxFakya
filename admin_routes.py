from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Product, ProductPricing
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def dashboard():
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

@admin_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')

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
            category=category,
            image_url=image_url
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
                    quantity=int(q),
                    price=float(p)
                )
                db.session.add(new_pricing)

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_product.html')

@admin_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.category = request.form.get('category')

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
                    quantity=int(q),
                    price=float(p)
                )
                db.session.add(new_pricing)

        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_product.html', product=product)

@admin_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('admin.dashboard'))
