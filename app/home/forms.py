from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    user = StringField(validators=[DataRequired()])
    submit = SubmitField("Get your stats!")
