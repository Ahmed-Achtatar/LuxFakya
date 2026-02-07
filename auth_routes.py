from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, UserLog

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

            # Log successful login
            try:
                log = UserLog(
                    user_id=user.id,
                    action='login',
                    details=f"User logged in from IP: {request.remote_addr}"
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                # Don't fail login if logging fails
                pass

            flash('Logged in successfully.', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                 return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        else:
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
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check email uniqueness if changed
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use by another account.', 'danger')
                return redirect(url_for('auth.profile'))

        current_user.email = email
        current_user.full_name = full_name
        current_user.phone = phone
        current_user.address = address
        current_user.city = city

        if new_password:
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
            else:
                current_user.set_password(new_password)
                flash('Password updated.', 'success')

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate token
            from itsdangerous import URLSafeTimedSerializer
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='recover-key')

            # Log the link
            link = url_for('auth.reset_password', token=token, _external=True)
            print(f"PASSWORD RESET LINK for {email}: {link}")
            current_app.logger.info(f"PASSWORD RESET LINK for {email}: {link}")

            flash('Password reset link has been sent to your email (Check console/logs).', 'info')
        else:
            flash('Email not found.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='recover-key', max_age=3600)
    except SignatureExpired:
        flash('The token is expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    except Exception:
        flash('The token is invalid.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
             flash('Passwords do not match.', 'danger')
             return redirect(url_for('auth.reset_password', token=token))

        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('auth.login'))
        else:
             flash('User not found.', 'danger')
             return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')
