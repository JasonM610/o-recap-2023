import os
from flask import Flask
from .home import routes
from .users import routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # with app.app_context():
    app.register_blueprint(home.routes.home_bp)
    app.register_blueprint(users.routes.users_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
