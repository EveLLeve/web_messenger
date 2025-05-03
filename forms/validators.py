from wtforms.validators import ValidationError
from data.user import User
from data.db_session import create_session

def unique_username(form, field):
    db_sess = create_session()
    if db_sess.query(User).filter_by(username=field.data).first():
        raise ValidationError('Это имя пользователя уже занято!')
