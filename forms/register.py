from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Введите почту*', validators=[DataRequired()])
    username = StringField('Введите имя пользователя*', validators=[DataRequired()])
    password = PasswordField('Пароль*', validators=[DataRequired()])
    submit_password = PasswordField('Повоторите пароль*', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
