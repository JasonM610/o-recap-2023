from flask import Blueprint, redirect, render_template, url_for
from typing import Union
from . import create_app
from .forms import UserForm

app = Blueprint("app", __name__)


@app.route("/", methods=["GET", "POST"])
def index():
    form = UserForm()
    if form.validate_on_submit():
        user = form.user.data
        mode = form.mode.data

        # if user isn't in database

        return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user=user)


@app.route("/users/<user>/", methods=["GET"])
def user(user: Union[int, str]):
    # query the database for the appropriate data. return error page if not in
    return render_template(
        "user.html", user_data=user_data, best_perfs=best_perfs, score_stats=stats
    )
