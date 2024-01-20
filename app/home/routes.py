from flask import Blueprint, redirect, render_template, url_for
from app.home.forms import UserForm
from app.utils.db import Dynamo


home = Blueprint(
    "home",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/home/static",
)


@home.route("/", methods=["GET", "POST"])
def index():
    form = UserForm()
    db = Dynamo()

    if form.validate_on_submit():
        user_input = form.user.data.strip()
        return redirect(url_for("users.user", user=user_input))

    return render_template("index.html", form=form, queue_size=db.get_queue_size())
