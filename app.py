# app.py
from flask import Flask
from config import Config
from extensions import db, login_manager, mail
from flask_migrate import Migrate
from flask_login import current_user
from models import Notification  # ensures models are registered
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ================= MAIL CONFIG =================
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = "fadiliddrisu24@gmail.com"
    app.config["MAIL_PASSWORD"] = "vwba szck lpcb uvis"  # Gmail App password
    app.config["MAIL_DEFAULT_SENDER"] = "fadiliddrisu24@gmail.com"

    # ================= EXTENSIONS =================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    mail.init_app(app)
    Migrate(app, db)

    # ================= BLUEPRINTS =================
    from auth.routes import auth_bp
    from admin_bp import admin_bp  # make sure your blueprint inside admin/routes.py is named admin_bp
    from courses.routes import courses_bp
    from groups.routes import groups_bp
    from home_bp import home_bp
    from library.routes import library_bp
    from notifications.routes import notifications_bp
    from dashboard_bp import dashboard_bp
    from quiz_bp import quiz_bp
    from routes.users_bp import users_bp
    from legal_bp import legal_bp

    # Register blueprints (no duplicates!)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")  # only once
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(groups_bp, url_prefix="/groups")
    app.register_blueprint(home_bp)  # main home page
    app.register_blueprint(library_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(users_bp)
    app.register_blueprint(legal_bp)

    # ================= CONTEXT PROCESSOR =================
    @app.context_processor
    def inject_unread_notifications():
        if current_user.is_authenticated:
            count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
        else:
            count = 0
        return dict(unread_notifications=count)

    return app


# ================= RUN =================
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
