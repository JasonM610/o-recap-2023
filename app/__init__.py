import os
from flask import Flask
from . import routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    app.register_blueprint()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
