import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "college.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads", "test_proofs")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB per upload
    app.config["ALLOWED_UPLOAD_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "pdf", "heic"}

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.applications import applications_bp
    from routes.notes import notes_bp
    from routes.contacts import contacts_bp
    from routes.campus import campus_bp
    from routes.schools import schools_bp
    from routes.scholarships import scholarships_bp
    from routes.financial_aid import financial_aid_bp
    from routes.calendar import calendar_bp
    from routes.community import community_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(campus_bp)
    app.register_blueprint(schools_bp)
    app.register_blueprint(scholarships_bp)
    app.register_blueprint(financial_aid_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(community_bp)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year, "site_name": "CollegeOneStop"}

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5002)
