from flask import Blueprint, redirect, render_template, url_for
import asyncio
from app import db
from app.home.forms import UserForm
from app.utils.api import get_user_data, get_best_scores
from app.utils.beatmaps import insert_all_scores


home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates", static_folder="static"
)


@home_bp.route("/", methods=["GET", "POST"])
def index():
    user_input = False
    form = UserForm()

    if form.validate_on_submit():
        user_input = form.user.data
        mode_input = form.mode.data

        user = get_user_data(user_input, mode_input)
        user_id = user.user_id
        user_in_db = user.upsert()

        if not user_in_db:
            for best_score, score, beatmap in get_best_scores(user_id, mode_input):
                beatmap.add_if_not_exists()
                score.add_if_not_exists()
                db.session.add(best_score)

        db.session.commit()
        asyncio.create_task(insert_all_scores(user_id, mode_input))

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user_input=user_input)
