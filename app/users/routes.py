from flask import Blueprint, redirect, render_template, url_for
from app.utils.osu import get_user
from app.utils.analytics import get_profile

users = Blueprint(
    "users",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/users/static",
)


@users.route("/users/<user_id>", methods=["GET"])
def user(user_id):
    if not user_id.isdigit():
        user = get_user(user_id)
        return redirect(url_for("users.user", user_id=user.user_id))

    user_data = get_profile(int(user_id))
    if user_data is None:
        # ?
        return render_template("user.html")

    return render_template("user.html", user=user_data)
