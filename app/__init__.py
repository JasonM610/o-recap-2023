from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .views import main

db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(main)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
