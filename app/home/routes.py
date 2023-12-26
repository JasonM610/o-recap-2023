import boto3
from flask import Blueprint, flash, redirect, render_template, url_for
from app.home.forms import UserForm
from app.utils.osu import get_user
from app.utils.analytics import insert_user_and_enqueue
from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_QUEUE_URL


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

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    sqs = session.resource("sqs")
    queue = sqs.Queue(AWS_QUEUE_URL)
    queue_size = queue.attributes["ApproximateNumberOfMessages"]

    if form.validate_on_submit():
        user_input = form.user.data
        user = get_user(user_input)

        if user is None:
            flash("User not found. Please enter a valid username/ID")
            form.user.data = ""
            return render_template("index.html", form=form, queue_size=queue_size)

        insert_user_and_enqueue(user)
        return redirect(url_for("users.user", user=user.user_id))

    return render_template("index.html", form=form, queue_size=queue_size)
