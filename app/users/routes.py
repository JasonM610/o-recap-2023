from flask import Blueprint, redirect, render_template, url_for

users_bp = Blueprint(
    "users_bp", __name__, template_folder="templates", static_folder="static"
)


@users_bp.route("/users/<user>/<mode>", methods=["GET"])
def user():
    return
