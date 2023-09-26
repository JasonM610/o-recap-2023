from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import boto3

db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():
        from .home import routes
        from .users import routes

        app.register_blueprint(home.routes.home_bp)
        app.register_blueprint(users.routes.users_bp)

        db.create_all()

        sqs = boto3.client("sqs", region_name=app.config.REGION)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
