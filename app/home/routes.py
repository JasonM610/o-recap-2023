from flask import Blueprint, flash, redirect, render_template, url_for
from app.home.forms import UserForm
from app.utils.osu import get_user
from app.utils.analytics import insert_user_and_enqueue


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

        user = get_user(user_input)
        if user is None:
            flash("User not found!")
            return render_template("index.html", form=form)

        insert_user_and_enqueue(user)

        return redirect(url_for("users.index", user_id=user.user_id))

    return render_template("index.html", form=form)
