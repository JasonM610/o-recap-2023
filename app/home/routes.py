from flask import Blueprint, flash, redirect, render_template, url_for
from app import db
from app.home.forms import UserForm
from app.utils.osu import get_user_data, get_best_scores
from app.utils.analytics import insert_data_and_enqueue


home = Blueprint(
    "home",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/home/static",
)


@home.route("/", methods=["GET", "POST"])
def index():
    user_input = False
    form = UserForm()

    if form.validate_on_submit():
        user_input = form.user.data
        mode_input = form.mode.data

        user = get_user_data(user_input)
        if user is None:
            flash("User not found!")
            return render_template("index.html", form=form)

        user_id = user.user_id
        user_in_db = user.insert_or_update()

        if not user_in_db:
            best_scores = get_best_scores(user_id)
            insert_data_and_enqueue(user, best_scores)

            for best_score in best_scores:
                best_score.add_if_not_exists()

        db.session.commit()

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form)
