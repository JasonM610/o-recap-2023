from flask import Blueprint, redirect, render_template, url_for
from app.utils.analytics import get_profile, get_id_from_username

users = Blueprint(
    "users",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/users/static",
)


@users.route("/users/<user>", methods=["GET"])
def user(user):
    if not user.isdigit():
        user_id = get_id_from_username(user)
        if user_id == -1:
            return render_template("user.html", user=None)
        return redirect(url_for("users.user", user=user_id))

    user_data = get_profile(int(user))
    return render_template("user.html", user=user_data)
