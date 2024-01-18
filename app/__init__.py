from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.from_object("config.Config")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    with app.app_context():
        from .home import routes
        from .users import routes

        app.register_blueprint(home.routes.home)
        app.register_blueprint(users.routes.users)

        return app


app = create_app()
