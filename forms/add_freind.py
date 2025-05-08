from flask_wtf import FlaskForm
from wtforms.fields.simple import SearchField, SubmitField
from wtforms.validators import DataRequired


class FriendForm(FlaskForm):
    username = SearchField('Добавить друзей', validators=[DataRequired()])
    submit1 = SubmitField('Отправить запрос')
