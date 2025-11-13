from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Book, CartItem

main = Blueprint('main', __name__)

# Health check endpoints for OpenShift
@main.route('/health')
def health():
    """Liveness probe - checks if app is running"""
    return jsonify({'status': 'healthy'}), 200

@main.route('/ready')
def ready():
    """Readiness probe - checks if app is ready to serve traffic"""
    try:
        # Check database connectivity
        db.session.execute(db.select(User).limit(1))
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503

# Homepage
@main.route('/')
def index():
    """Homepage with featured books"""
    books = Book.query.limit(6).all()
    return render_template('index.html', books=books)

# Catalogue
@main.route('/catalogue')
def catalogue():
    """Book catalogue page with all books"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('catalogue.html', books=pagination.items, pagination=pagination)

# Book detail
@main.route('/book/<int:book_id>')
def book_detail(book_id):
    """Individual book detail page"""
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

# Authentication routes
@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('main.index'))

# Shopping cart routes
@main.route('/cart')
@login_required
def cart():
    """View shopping cart"""
    cart_items = current_user.cart_items
    total = current_user.get_cart_total()
    return render_template('cart.html', cart_items=cart_items, total=total)

@main.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    """Add book to cart"""
    book = Book.query.get_or_404(book_id)

    # Check if book already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, book_id=book_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'Added "{book.title}" to cart', 'success')
    return redirect(request.referrer or url_for('main.catalogue'))

@main.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.get_or_404(item_id)

    if cart_item.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('main.cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart', 'info')
    return redirect(url_for('main.cart'))

@main.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_quantity(item_id):
    """Update quantity of cart item"""
    cart_item = CartItem.query.get_or_404(item_id)

    if cart_item.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('main.cart'))

    quantity = request.form.get('quantity', type=int)
    if quantity and quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated', 'success')
    else:
        flash('Invalid quantity', 'danger')

    return redirect(url_for('main.cart'))

@main.route('/checkout')
@login_required
def checkout():
    """Simple checkout page"""
    if not current_user.cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.catalogue'))

    total = current_user.get_cart_total()
    return render_template('checkout.html', cart_items=current_user.cart_items, total=total)

@main.route('/checkout/complete', methods=['POST'])
@login_required
def complete_checkout():
    """Complete checkout (simplified - no payment processing)"""
    if not current_user.cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.catalogue'))

    # Clear cart
    for item in current_user.cart_items:
        db.session.delete(item)

    db.session.commit()
    flash('Order completed successfully! Thank you for your purchase.', 'success')
    return redirect(url_for('main.index'))
