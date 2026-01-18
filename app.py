import os
import sys
import logging
from flask import Flask, session, request, send_from_directory, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User, Category
from translations import translations

def create_app(test_config=None):
    app = Flask(__name__)

    # Configure logging
    if not app.debug:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
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
    login_manager.login_view = 'admin.login'
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
        return jsonify({'status': 'healthy', 'message': 'Application is running'}), 200

    # Register Blueprints
    from routes import main_bp
    from admin_routes import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

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

        return dict(
            get_text=get_text,
            current_lang=lang,
            text_dir='rtl' if lang == 'ar' else 'ltr',
            all_categories=categories
        )

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database connection failed: {e}")
            print(f"CRITICAL ERROR: Database connection failed: {e}", file=sys.stderr)
            # We do NOT re-raise, so the app can start and serve /health

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
