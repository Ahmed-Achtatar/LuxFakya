from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, send_file, jsonify
from flask_login import current_user
from models import Product, db, Order, OrderItem, HomeSection, Category, DbImage, UserLog
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/db_image/<int:image_id>')
def get_db_image(image_id):
    image = DbImage.query.get_or_404(image_id)
    return send_file(
        io.BytesIO(image.data),
        mimetype=image.mimetype,
        as_attachment=False,
        download_name=image.filename
    )

@main_bp.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    if lang_code in ['fr', 'ar']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/')
def index():
    # Fetch all products to distribute across sections
    all_products = Product.query.filter_by(is_hidden=False).all()
    all_categories = Category.query.all()

    # Fetch Home Sections
    limited_offer = HomeSection.query.filter_by(section_name='limited_offer').first()
    hero_section = HomeSection.query.filter_by(section_name='hero').first()
    about_section = HomeSection.query.filter_by(section_name='about').first()
    promo_banner = HomeSection.query.filter_by(section_name='promo_banner').first()

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
                         featured_products=featured_collection,
                         all_products=all_products,
                         limited_offer=limited_offer,
                         hero_section=hero_section,
                         about_section=about_section,
                         promo_banner=promo_banner,
                         all_categories=all_categories)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/shop')
def shop():
    category_name = request.args.get('category')
    if category_name:
        # Combine the JOIN strategy (from Current) with the hidden check (from Incoming)
        products = Product.query.join(Category).filter(
            Category.name == category_name,
            Product.is_hidden == False
        ).all()
    else:
        products = Product.query.filter_by(is_hidden=False).all()

    # Get all categories
    categories = Category.query.all()

    return render_template('shop.html', products=products, categories=categories, current_category=category_name)

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    # Related products strategy: Same category, exclude current
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
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
            # Calculate price logic
            item_total = product.price * quantity

            # Check for quantity-based pricing
            # Use float comparison tolerance if needed, but for now strict float equality for exact matches
            # from seed data (e.g. 1.0, 2.0)
            found_pricing = False
            for pricing in product.pricings:
                if pricing.quantity == quantity:
                    item_total = pricing.price
                    found_pricing = True
                    break

            # Format to 2 decimal places for display consistency
            item_total = round(item_total, 2)

            total_price += item_total
            cart_items.append({'product': product, 'quantity': quantity, 'total': item_total})

    total_price = round(total_price, 2)
    return render_template('cart.html', cart_items=cart_items, total=total_price)

@main_bp.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.is_out_of_stock:
        flash('This product is out of stock.', 'danger')
        return redirect(request.referrer or url_for('main.shop'))

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    pid = str(product_id)

    # Allow float quantity
    try:
        quantity = float(request.values.get('quantity', 1.0))
    except ValueError:
        quantity = 1.0

    if quantity <= 0:
        quantity = 1.0

    if pid in cart:
        cart[pid] += quantity
    else:
        cart[pid] = quantity

    session.modified = True
    current_app.logger.info(f"Added product {product_id} (qty: {quantity}) to cart")

    # Check for AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': f'Added {quantity} item(s) to cart',
            'cart_count': len(cart)
        })

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

    try:
        quantity = float(request.form.get('quantity', 1.0))
    except ValueError:
        quantity = 1.0

    if quantity <= 0:
        return remove_from_cart(product_id)

    cart = session['cart']
    pid = str(product_id)
    cart[pid] = quantity
    session.modified = True

    return redirect(url_for('main.cart'))

@main_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('main.shop'))

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')

        cart = session['cart']
        total_price = 0
        order_items = []

        # Calculate total and prepare items
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = product.price * quantity

                # Pricing logic
                for pricing in product.pricings:
                    if pricing.quantity == quantity:
                        item_total = pricing.price
                        break

                total_price += item_total

                order_item = OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    unit=product.unit,
                    price_at_purchase=item_total/quantity if quantity > 0 else 0 # Unit price roughly or total
                )
                # Store the effective unit price based on the total calculated with tier pricing
                order_item.price_at_purchase = item_total / quantity if quantity > 0 else 0
                order_items.append(order_item)

        new_order = Order(
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            customer_address=address,
            customer_city=city,
            total_amount=round(total_price, 2),
            status='Pending'
        )

        if current_user.is_authenticated:
            new_order.user_id = current_user.id

        db.session.add(new_order)
        db.session.commit()

        for item in order_items:
            item.order_id = new_order.id
            db.session.add(item)

        db.session.commit()

        current_app.logger.info(f"Order created: {new_order.id} for {name} ({total_price})")

        # User Tracking: Log order creation
        try:
            log = UserLog(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='purchase_attempt',
                details=f"Order {new_order.id} created. Total: {total_price}. Customer: {name}"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log purchase: {e}")

        # Clear cart
        session.pop('cart', None)

        return redirect(url_for('main.order_confirmation', order_id=new_order.id))

    return render_template('checkout.html')

@main_bp.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)
