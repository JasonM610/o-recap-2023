from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.utils.enums import Mode


class UserForm(FlaskForm):
    user = StringField(validators=[DataRequired()])
    mode = SelectField(
        choices=[
            ("osu", "osu"),
            ("taiko", "Taiko"),
            ("fruits", "CTB"),
            ("mania", "Mania"),
        ],
    )
    submit = SubmitField("Get your stats!")
