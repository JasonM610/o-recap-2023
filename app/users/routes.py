from flask import Blueprint, jsonify, request, render_template
from app.utils.analytics import get_profile

users = Blueprint(
    "users",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/users/static",
)


@users.route("/users/<user_id>", methods=["GET"])
def index(user_id):
    user_data = get_profile(int(user_id))
    return jsonify(user_data)
