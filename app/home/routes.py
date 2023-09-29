from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from app import db, sqs
from app.home.forms import UserForm
from app.utils.api import get_user_data, get_best_scores


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

        user = get_user_data(user_input, mode_input)
        if user:
            user_id = user.user_id
            user_in_db = user.upsert()

            if not user_in_db:
                best_scores, scores, beatmaps = get_best_scores(user_id, mode_input)

                for beatmap, score in zip(beatmaps, scores):
                    beatmap.add_if_not_exists()
                    score.add_if_not_exists()
                db.session.add_all(best_scores)

                # send to SQS. comment out for now
                # sqs.send_message(
                # QueueUrl=current_app.config["QUEUE_URL"], MessageBody=str(user_id)
                # )

            db.session.commit()
        else:
            flash("User not found!")

        # return redirect(url_for("user", user=user))

    return render_template("index.html", form=form, user_input=user_input)
