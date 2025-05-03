import os

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_restful import Api

from flask import Flask, render_template, redirect, request, abort, jsonify

from data import db_session
from data.chats import Chats
from data.messages import Message
from data.user import User
from forms.chat import ChatForm
from forms.login import LoginForm
from forms.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


def add_user(db_sess, username, name, surname, email, password):
    user = User()
    user.name = name.data
    user.username = username.data.strip()
    user.email = email.data
    user.set_password(password.data)
    user.surname = surname.data
    db_sess.add(user)
    db_sess.commit()
    return user


def add_message(db_sess, content, creator):
    message = Message()
    message.content = content
    message.creator = creator
    db_sess.add(message)
    db_sess.commit()


def add_chat(db_sess, name, members):
    chat = Chats()
    chat.name = name
    for member in members:
        user = db_sess.query(User).filter(User.username == member).first()
        chat.users.append(user)
    db_sess.add(chat)
    db_sess.commit()
    return chat


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
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
    user = db_ses.query(User).filter(User.username==username).first()
    return jsonify({'exists': user is not None})


@app.route('/check_email', methods=['POST'])
def check_email():
    db_ses = db_session.create_session()
    email = request.form.get('email').strip()
    user = db_ses.query(User).filter(User.email==email).first()
    return jsonify({'exists': user is not None})


@app.route('/')
def index():
    chats = []
    usernames = []
    if current_user.is_authenticated:
        id_user = current_user.id
        db_sess = db_session.create_session()
        users = db_sess.query(User.username).all()
        for i in users:
            usernames.append(i[0])
        chats = db_sess.query(Chats).filter(Chats.users.any(User.id == id_user)).all()
    return render_template('index.html', usernames=usernames, title='', chats=chats)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.password.data == form.submit_password.data:
            img = 'static/img/users/default.png'
            user = add_user(db_sess, form.username, form.name, form.surname, form.email, form.password)
            photo = form.photo.data.read()
            if photo:
                img = f'static/img/users/user{user.id}.{form.photo.data.filename[form.photo.data.filename.rfind(".") + 1:]}'
                with open(img, 'wb') as f:
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
    form = ChatForm()
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if current_user.friends:
            friends = current_user.friends.split(', ')
            form.members.choices = friends
        if form.validate_on_submit():
            img = 'static/img/group/default_group.avif'
            members = form.members.data
            members.append(current_user.username)
            chat = add_chat(db_sess, form.name.data, members)
            photo = form.photo.data.read()
            if photo:
                img = f'static/img/group/chat{chat.id}.{form.photo.data.filename[form.photo.data.filename.rfind(".") + 1:]}'
                with open(img, 'wb') as f:
                    f.write(photo)
            chat.chat_image = img
            db_sess.commit()
            return redirect(f"/chat/{chat.id}")
        return render_template('create_chat.html', title='klk', form=form)
    return redirect('/login')


def main():
    db_session.global_init("db/chat.sqlite")

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
