from flask import url_for
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from data import db_session
from data.func import add_message
from data.user import User


def initialization(socketio):
    @socketio.on('message')
    def handle_message(data, user, chat):
        m = ''
        if current_user.id == user:
            db = db_session.create_session()
            m = add_message(db, data, db.get(User, user), chat)
        emit('message', (str(data), m.users[0].username, url_for('static', filename=m.users[0].profile_picture),
                         str(m.created_date.strftime('%d.%m.%y %H:%M'))), room=m.chat_id)

    @socketio.on('join')
    def handle_join(data):
        """Подключение пользователя к комнате"""
        room = data['room_id']
        join_room(room)  # Добавляем в комнату
        emit('system_message', f'Вы вошли в чат {room}', room=room)
