import os
import sys
from flask import Flask, session, request, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User, Category
from translations import translations

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-luxfakia')

    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Log that we found a DB URL (masking credentials)
        masked_url = database_url.split('@')[-1] if '@' in database_url else '***'
        print(f"Using configured Database: ...@{masked_url}", file=sys.stderr)

        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        print("WARNING: No DATABASE_URL found. Using local SQLite. Data will be lost on restart in production environments like Railway.", file=sys.stderr)

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

    # Health Check Route
    @app.route('/health')
    def health_check():
        try:
            # Simple query to verify DB connection
            db.session.execute(db.text('SELECT 1'))
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            print(f"Health check failed: {e}", file=sys.stderr)
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    # Register Blueprints
    from routes import main_bp
    from admin_routes import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_global_context():
        lang = session.get('lang', 'fr')
        def get_text(key):
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
            print("Database tables verified.", file=sys.stderr)

            # Check if database is empty (no categories)
            if not app.config.get('TESTING') and Category.query.first() is None:
                print("Database appears empty. Starting auto-seeding...", file=sys.stderr)
                try:
                    from seed import seed_data
                    seed_data()
                    print("Auto-seeding completed successfully.", file=sys.stderr)
                except Exception as seed_error:
                    print(f"ERROR: Auto-seeding failed: {seed_error}", file=sys.stderr)

        except Exception as e:
            print(f"CRITICAL: Database connection failed during startup: {e}", file=sys.stderr)
            # We don't exit here so the app can at least start and serve /health with error

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
