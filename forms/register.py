from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired
from forms.validators import unique_username


class RegisterForm(FlaskForm):
    email = EmailField('Введите почту', validators=[DataRequired()])
    photo = FileField()
    username = StringField('Введите имя пользователя(не более 50 символов)', validators=[DataRequired(), unique_username])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit_password = PasswordField('Повоторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия(необязательно)')
    name = StringField('Имя(необязательно)')
    submit = SubmitField('Подтвердить')
