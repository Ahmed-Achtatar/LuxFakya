from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', 'customer') == 'admin':
             return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')

        # Check by username or email
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user and user.check_password(password):
            login_user(user)

            # Log Login Success
            from models import UserLog
            log = UserLog(
                user_id=user.id,
                action='Login Successful',
                ip_address=request.remote_addr,
                details=f"User {user.username} logged in."
            )
            db.session.add(log)
            db.session.commit()

            flash('Logged in successfully.', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                 return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        else:
            # Log Login Failure
            from models import UserLog
            log = UserLog(
                user_id=None,
                action='Login Failed',
                ip_address=request.remote_addr,
                details=f"Failed login attempt for username/email: {username_or_email}"
            )
            db.session.add(log)
            db.session.commit()

            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            role='customer'
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Registration successful! Welcome.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')

        # Check email uniqueness if changed
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use by another account.', 'danger')
                return redirect(url_for('auth.profile'))

        current_user.email = email

        # Check username uniqueness if changed
        username = request.form.get('username')
        if username and username != current_user.username:
             if User.query.filter_by(username=username).first():
                 flash('Username already in use.', 'danger')
                 return redirect(url_for('auth.profile'))
             current_user.username = username

        current_user.full_name = full_name
        current_user.phone = phone
        current_user.address = address
        current_user.city = city

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        # Dummy flow
        flash(f'If an account exists for {email}, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')
