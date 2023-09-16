from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField


class UserForm(FlaskForm):
    user = StringField("Please enter your username or user ID:")
    mode = SelectField(
        "Gamemode: ",
        choices=[
            ("osu", "osu!"),
            ("taiko", "Taiko"),
            ("fruits", "CTB"),
            ("mania", "Mania"),
        ],
    )
    submit = SubmitField("Submit")
