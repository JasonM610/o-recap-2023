from flask import Blueprint, render_template
from app.utils.profiles import ProfileDAO

users = Blueprint(
    "users",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/users/static",
)


@users.route("/u/<user>", methods=["GET"])
def user(user):
    profiles = ProfileDAO()
    user_data = profiles.process_request(user)

    return render_template("user.html", user=user_data)
