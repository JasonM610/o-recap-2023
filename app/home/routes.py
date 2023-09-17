from flask import Blueprint, redirect, render_template, url_for
from flask import current_app as app
from .forms import UserForm


home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates", static_folder="static"
)


@home_bp.route("/", methods=["GET", "POST"])
def index():
    user = False
    form = UserForm()
    if form.validate_on_submit():
        user = form.user.data
        mode = form.mode.data

        # if user isn't in database

        return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user=user)
