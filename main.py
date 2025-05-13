import os

from cryptography.fernet import Fernet
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api

from flask import Flask, render_template, redirect, request, jsonify, url_for
from flask_socketio import SocketIO

from data import db_session, users_resource
from data.chats import Chats
from data.func import check_friend, add_user, add_chat, add_message
from data.notification import Notification
from data.user import User
from forms.chat import ChatForm
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.add_freind import FriendForm
from data.socket import initialization


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or Fernet.generate_key().decode()


app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app)
initialization(socketio)


def find_friends(db_sess):
    global reload
    form_friend = FriendForm()
    check = check_friend(form_friend)
    usernames = []
    users = db_sess.query(User.username).all()
    for i in users:
        usernames.append(i[0])
    if check:
        reload = True
        return True, check, usernames, form_friend
    get_a = reload
    reload = False
    check = request.args.get('check')
    return False, get_a, check, usernames, form_friend


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(
            (User.username == form.username.data) | (User.email == form.username.data)).all()
        for user in users:
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        return render_template('login.html',
                               message="Неправильный имя пользователя/почта или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/check_username', methods=['POST'])
def check_username():
    db_ses = db_session.create_session()
    username = request.form.get('username').strip()
    user = db_ses.query(User).filter(User.username == username).first()
    return jsonify({'exists': user is not None})


@app.route('/check_email', methods=['POST'])
def check_email():
    db_ses = db_session.create_session()
    email = request.form.get('email').strip()
    user = db_ses.query(User).filter(User.email == email).first()
    return jsonify({'exists': user is not None})


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        global reload

        h = find_friends(db_sess)
        if h[0]:
            return redirect(url_for('index', check=h[1]))
        get_a, check, usernames, form_friend = h[1:]
        id_user = current_user.id
        chat = db_sess.query(Chats).filter(Chats.users.any(User.id == id_user)).all()
        return render_template('index.html', title='Главная', usernames=usernames, reload=get_a, modal_message=check, chats=chat, form_friend=form_friend)
    return render_template('index.html', title='Главная')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.password.data == form.submit_password.data:
            img = 'img/users/default.png'
            user = add_user(db_sess, form.username, form.name, form.surname, form.email, form.password)
            photo = form.photo.data.read()
            if photo:
                img = (f'img/users/user{user.id}.' +
                       f'{form.photo.data.filename[form.photo.data.filename.rfind(".") + 1:]}')
                with open(f'static/{img}', 'wb') as f:
                    f.write(photo)
            user.profile_picture = img
            db_sess.commit()
            return redirect("/login")
        return render_template('register.html',
                               message="Пароли не совпадают",
                               form=form)
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/chat', methods=['GET', 'POST'])
def add_a_chat():
    if current_user.is_authenticated:
        form = ChatForm()
        db_sess = db_session.create_session()
        if current_user.friends:
            friends = current_user.friends.split(', ')
            form.members.choices = friends

        global reload

        h = find_friends(db_sess)
        if h[0]:
            return redirect(url_for('chats', check=h[1]))
        get_a, check, usernames, form_friend = h[1:]
        if form.validate_on_submit():
            img = 'img/group/default_group.avif'
            members = form.members.data
            members.append(current_user.username)
            chat = add_chat(db_sess, form.name.data, members)
            photo = form.photo.data.read()
            if photo:
                img = (f'img/group/chat{chat.id}.' +
                       f'{form.photo.data.filename[form.photo.data.filename.rfind(".") + 1:]}')
                with open(f'static/{img}', 'wb') as f:
                    f.write(photo)
            chat.chat_image = img
            db_sess.commit()
            return redirect(f"/chat/{chat.id}")
        return render_template('create_chat.html', form=form, usernames=usernames, reload=get_a, modal_message=check,
                               form_friend=form_friend)
    return redirect('/login')


@app.route('/chat/<int:id_chat>', methods=['GET', 'POST'])
def chats(id_chat):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        chat = db_sess.get(Chats, id_chat)
        global reload

        h = find_friends(db_sess)
        if h[0]:
            return redirect(url_for('chats', id_chat=id_chat, check=h[1]))
        get_a, check, usernames, form_friend = h[1:]
        if current_user.id not in map(lambda x: x.id, chat.users):
            return redirect(url_for('index'))
        return render_template('chating.html', chats=chat, usernames=usernames, reload=get_a,
                               modal_message=check, form_friend=form_friend, title=chat.name)
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect('/')
    db_sess = db_session.create_session()
    form = RegisterForm()
    if form.submit.data:
        user = add_user(db_sess, form.username, form.name, form.surname, form.email, add=False)
        photo = form.photo.data.read()
        if photo:
            img = (f'img/users/user{user.id}.' +
                   f'{form.photo.data.filename[form.photo.data.filename.rfind(".") + 1:]}')
            with open(f'static/{img}', 'wb') as f:
                f.write(photo)
            user.profile_picture = img
            db_sess.commit()
        return redirect('/profile')
    global reload

    h = find_friends(db_sess)
    if h[0]:
        return redirect(url_for('profile', check=h[1]))
    get_a, check, usernames, form_friend = h[1:]
    return render_template('profile.html', title='Профиль', form=form, usernames=usernames, reload=get_a,
                           modal_message=check, form_friend=form_friend)


@app.route('/chat/<int:id_chat>/settings', methods=['GET', 'POST'])
def chat_setting(id_chat):
    if current_user.is_authenticated:
        form = ChatForm()
        db_sess = db_session.create_session()
        chat = db_sess.get(Chats, id_chat)
        if current_user.friends:
            friends = current_user.friends.split(', ')
            form.members.choices = list(set(friends + [i.username for i in chat.users]))

        global reload

        h = find_friends(db_sess)
        if h[0]:
            return redirect(url_for('chats', check=h[1]))
        get_a, check, usernames, form_friend = h[1:]
        if form.submit.data:
            img = 'img/group/default_group.avif'
            members = form.members.data
            chat = add_chat(db_sess, form.name.data, members, False, id_chat)
            photo = form.photo.data.read()
            if photo:
                img = (f'img/group/chat{chat.id}.' +
                       f'{form.photo.data.filename[form.photo.data.filename.rfind(".") + 1:]}')
                with open(f'static/{img}', 'wb') as f:
                    f.write(photo)
            chat.chat_image = img
            db_sess.commit()
            return redirect(f"/chat/{chat.id}")
        return render_template('chat_setting.html', chat=chat, members=[i.username for i in chat.users], form=form, usernames=usernames, reload=get_a,
                               modal_message=check, form_friend=form_friend, title=f'Настроки чата: {chat.name}')
    return redirect(url_for('login'))


@app.route('/delete/<int:chat_id>')
def delete_chat(chat_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    db_sess = db_session.create_session()
    chat = db_sess.get(Chats, chat_id)
    if current_user in chat.users:
        db_sess.delete(chat)
        db_sess.commit()
    return redirect(url_for('index'))


@app.route('/friends', methods=['GET', 'POST'])
def friends_list():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    db_sess = db_session.create_session()
    friend = [i for i in db_sess.query(User).filter((User.username).in_(current_user.friends.split(', ')))]
    global reload
    h = find_friends(db_sess)
    if h[0]:
        return redirect(url_for('friends_list', check=h[1]))
    get_a, check, usernames, form_friend = h[1:]
    return render_template('friend.html', users=friend, title='Ваши друзья', usernames=usernames, reload=get_a,
                           modal_message=check, form_friend=form_friend)


@app.route('/notification', methods=['GET', 'POST'])
def notification():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    db_sess = db_session.create_session()
    notific = db_sess.query(Notification).filter(Notification.target == current_user.username).all()
    global reload
    h = find_friends(db_sess)
    if h[0]:
        return redirect(url_for('notification', check=h[1]))
    get_a, check, usernames, form_friend = h[1:]
    return render_template('notification.html', notification=notific, title='Заявки в друзья', usernames=usernames, reload=get_a,
                           modal_message=check, form_friend=form_friend)


@app.route('/delete/<int:notific_id>/<accept>')
def change_notific(notific_id, accept):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    db_sess = db_session.create_session()
    notific = db_sess.get(Notification, notific_id)
    if current_user.username == notific.target:
        if accept == 'True':
            print(2)
            creator = db_sess.query(User).filter(User.username==notific.creator).first()
            target = db_sess.query(User).filter(User.username==notific.target).first()
            creator.friends += f', {target.username}'
            target.friends += f', {creator.username}'
        print(1)
        db_sess.delete(notific)
        db_sess.commit()
    return redirect(url_for('notification'))


def main():
    db_session.global_init("db/chat.sqlite")
    api.add_resource(users_resource.UserResource, '/api/user')
    api.add_resource(users_resource.UserListResource, '/api/users')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    reload = False
    main()
