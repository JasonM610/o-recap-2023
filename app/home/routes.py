from flask import Blueprint, redirect, render_template, url_for
from app.home.forms import UserForm
from app.utils.api import get_user_data, get_best_scores


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
        user_data = get_user_data(user, mode)
        best_scores_data = get_best_scores(user, mode)

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user=user)
