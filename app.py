import os
import sys
import logging
import traceback
from flask import Flask, session, request, send_from_directory, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User, Category
from translations import translations

def create_app(test_config=None):
    app = Flask(__name__)

    # Configure logging
    if not app.debug:
        # Check if gunicorn handlers are present
        gunicorn_logger = logging.getLogger('gunicorn.error')
        if gunicorn_logger.handlers:
            app.logger.handlers = gunicorn_logger.handlers
            app.logger.setLevel(gunicorn_logger.level)
        else:
            # Fallback to stdout if not running under gunicorn or no handlers found
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)
            app.logger.setLevel(logging.INFO)

    app.logger.info(f"Application starting... Environment: {'Production' if not app.debug else 'Debug'}")

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-luxfakia')

    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///luxfakia.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    csrf = CSRFProtect()
    csrf.init_app(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/health')
    def health_check():
        app.logger.info("Health check endpoint called")
        return jsonify({'status': 'healthy', 'message': 'Application is running'}), 200

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Page not found: {request.url}")
        return "Page Not Found", 404

    # Register Blueprints
    from routes import main_bp
    from admin_routes import admin_bp
    from auth_routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    from models import HomeSection # Import here to avoid circular dependency if possible

    @app.context_processor
    def inject_global_context():
        lang = session.get('lang', 'fr')
        def get_text(key):
            # Fallback to key if translation missing, or fallback to FR/EN if needed?
            # Ideally fallback to English or the key itself.
            return translations.get(lang, {}).get(key, key)

        try:
            categories = Category.query.all()
        except Exception:
            categories = []

        try:
            promo = HomeSection.query.filter_by(section_name='promo_banner').first()
        except Exception:
            promo = None

        return dict(
            get_text=get_text,
            translations=translations,
            current_lang=lang,
            text_dir='rtl' if lang == 'ar' else 'ltr',
            all_categories=categories,
            promo_banner=promo
        )

    with app.app_context():
        try:
            db.create_all()

            # Auto-fix database schema (add missing columns)
            try:
                from fix_db import run_db_fix
                run_db_fix(app.config['SQLALCHEMY_DATABASE_URI'])
            except Exception as e:
                app.logger.error(f"Database schema fix failed: {e}")

        except Exception as e:
            app.logger.error(f"Database connection failed: {e}")
            print(f"CRITICAL ERROR: Database connection failed: {e}", file=sys.stderr)
            # We do NOT re-raise, so the app can start and serve /health

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
