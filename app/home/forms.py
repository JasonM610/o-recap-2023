from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.utils.enums import Mode


class UserForm(FlaskForm):
    user = StringField("User ID: ", validators=[DataRequired()])
    mode = SelectField(
        "Gamemode: ",
        choices=[
            ("osu", "osu"),
            ("taiko", "Taiko"),
            ("fruits", "CTB"),
            ("mania", "Mania"),
        ],
    )
    submit = SubmitField("Submit")
