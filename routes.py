from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Product, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch all products to distribute across sections
    all_products = Product.query.all()

    # Simulate different collections
    # In a real app, these would be filtered by date added, sales count, etc.
    new_arrivals = all_products[:4]
    best_sellers = all_products[4:8] if len(all_products) > 4 else all_products[:4]
    popular_items = all_products[2:6] if len(all_products) > 6 else all_products[:4]

    # For the main grid
    featured_collection = all_products[:4]

    return render_template('index.html',
                         new_arrivals=new_arrivals,
                         best_sellers=best_sellers,
                         popular_items=popular_items,
                         featured_products=featured_collection)

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

    # Related products strategy: Same category, exclude current
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(3).all()

    # Fallback to fill up to 3 items
    if len(related_products) < 3:
        exclude_ids = [p.id for p in related_products] + [product.id]
        more_products = Product.query.filter(Product.id.notin_(exclude_ids)).limit(3 - len(related_products)).all()
        related_products.extend(more_products)

    return render_template('product_detail.html', product=product, related_products=related_products)

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

@main_bp.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    pid = str(product_id)

    quantity = int(request.values.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    if pid in cart:
        cart[pid] += quantity
    else:
        cart[pid] = quantity

    session.modified = True
    flash(f'Added {quantity} item(s) to cart', 'success')
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
