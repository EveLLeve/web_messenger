from flask_wtf import FlaskForm
from wtforms.fields.simple import PasswordField, FileField, SubmitField, StringField
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    name = StringField('name of chat', validators=[DataRequired()])
    members = PasswordField('members', validators=[DataRequired()])
    photo = FileField('add photo')
    submit = SubmitField('create')
