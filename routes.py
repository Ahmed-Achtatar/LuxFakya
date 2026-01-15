from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Product, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Featured products or categories
    # For LuxFakia, maybe show top 3 dates, nuts, spices
    featured_products = Product.query.limit(6).all()
    return render_template('index.html', featured_products=featured_products)

@main_bp.route('/shop')
def shop():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()

    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('shop.html', products=products, categories=categories, current_category=category)

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@main_bp.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = {}

    cart_items = []
    total_price = 0

    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            total_price += product.price * quantity
            cart_items.append({'product': product, 'quantity': quantity})

    return render_template('cart.html', cart_items=cart_items, total=total_price)

@main_bp.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    # cart keys are strings in json session
    pid = str(product_id)

    if pid in cart:
        cart[pid] += 1
    else:
        cart[pid] = 1

    session.modified = True
    flash('Item added to cart', 'success')
    return redirect(request.referrer or url_for('main.shop'))

@main_bp.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' not in session:
        return redirect(url_for('main.cart'))

    cart = session['cart']
    pid = str(product_id)

    if pid in cart:
        del cart[pid]
        session.modified = True
        flash('Item removed from cart', 'info')

    return redirect(url_for('main.cart'))

@main_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if 'cart' not in session:
        return redirect(url_for('main.cart'))

    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        return remove_from_cart(product_id)

    cart = session['cart']
    pid = str(product_id)
    cart[pid] = quantity
    session.modified = True

    return redirect(url_for('main.cart'))
