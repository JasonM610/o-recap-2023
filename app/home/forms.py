from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from app.utils.osu import get_user


class UserForm(FlaskForm):
    user = StringField(validators=[DataRequired()])
    submit = SubmitField("Get your stats!")
