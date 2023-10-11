import os
from flask import Blueprint, flash, redirect, render_template, url_for
from app import db, sqs
from app.home.forms import UserForm
from app.utils.osu import get_user_data, get_best_scores


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

        # need logic for if existing user submits to a new mode
        if not user_in_db:
            best_scores = get_best_scores(user_id, mode_input)

            for best_score in best_scores:
                best_score.add_if_not_exists()

            message_body = {"UserID": str(user_id), "Mode": str(mode_input)}
            # sqs.send_message(
            # QueueUrl=os.environ.get("QUEUE_URL"), MessageBody=message_body
            # )

        db.session.commit()

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form)
