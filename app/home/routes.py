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

        user_data = get_user_data(user, mode)

        # if user isn't in database
        score_data, beatmap_data, top_play_data = get_best_scores(user, mode)

        # insert score beatmap & top play into db, merge user data if name was changed

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user=user)
