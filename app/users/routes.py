from flask import Blueprint, redirect, render_template, url_for

users = Blueprint(
    "users",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/users/static",
)


@users.route("/users/<user>/<mode>", methods=["GET"])
def user():
    return
