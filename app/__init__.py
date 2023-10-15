from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():
        from .home import routes
        from .users import routes

        app.register_blueprint(home.routes.home)
        app.register_blueprint(users.routes.users)

        db.create_all()

        return app


if __name__ == "__main__":
    app = create_app()
    app.run()
