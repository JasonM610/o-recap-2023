from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    user = StringField(validators=[DataRequired()])
