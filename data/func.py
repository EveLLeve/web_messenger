from flask_login import current_user

from data import db_session
from data.chats import Chats
from data.messages import Message
from data.notification import Notification
from data.user import User


def add_user(db_sess, username, name, surname, email, password='', add=True):
    if add:
        user = User()
    else:
        user = db_sess.query(User).filter(User.username == username.data).first()
    user.name = name.data
    user.username = username.data.strip()
    user.email = email.data
    if password:
        user.set_password(password.data)
    user.surname = surname.data
    if add:
        db_sess.add(user)
    db_sess.commit()
    return user


def add_message(db_sess, content, user, chat_id):
    message = Message()
    message.content = content
    message.chat_id = chat_id
    message.users.append(user)
    db_sess.add(message)
    chat = db_sess.get(Chats, message.chat_id)
    chat.last_date = message.created_date
    db_sess.commit()
    return message


def add_chat(db_sess, name, members, add=True, chat_id=0):
    if add:
        chat = Chats()
    else:
        chat = db_sess.get(Chats, chat_id)
        for member in chat.users:
            if member.username not in members:
                print(member, 1)
                chat.users.remove(member)
    for member in members:
        user = db_sess.query(User).filter(User.username == member).first()
        if member not in [i.username for i in chat.users]:
            print(member, 2)
            chat.users.append(user)
    chat.name = name
    if add:
        db_sess.add(chat)
    db_sess.commit()
    return chat


def check_friend(form):
    if form.submit1.data:
        db_sess = db_session.create_session()
        u = form.username.data.strip()
        user = db_sess.query(User).filter(User.username == u).first()
        if user:
            notific = Notification()
            notific.creator = current_user.username
            notific.target = user.username
            n = db_sess.query(Notification).filter((Notification.creator == notific.creator) & (Notification.target == notific.target)).first()
            if n:
                return 'Вы уже отправили запрос в друзья'
            if current_user.friends:
                fr = user.username in current_user.friends
                if fr:
                    return 'У вас уже есть такой друг'
            db_sess.add(notific)
            db_sess.commit()
            return 'Запрос успешно отправлен'
        return 'Пользователя с таким именем ещё нет'
    return ''
