from flask import Blueprint, redirect, render_template, url_for
from app.home.forms import UserForm
from app.utils.api import get_user_data, get_best_scores
from app.utils.enums import Mode

home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates", static_folder="static"
)


@home_bp.route("/", methods=["GET", "POST"])
def index():
    user_input = False
    form = UserForm()
    if form.validate_on_submit():
        user_input = form.user.data
        mode_input = Mode(form.mode.data)

        # collect user data from osu! api. store user_id for score endpoint
        user = get_user_data(user_input, mode_input)
        user.upsert()

        user_id = user.user_id

        # if user isn't in database
        top_plays, scores, beatmaps = get_best_scores(user_id, mode_input)

        # insert score beatmap & top play into db, merge user data if name was changed

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user_input=user_input)
