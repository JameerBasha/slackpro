from app.main import bp
from flask import render_template,url_for,flash,request,redirect
from app import db
from app.models import UserTable,GroupTable,Message
from flask_login import current_user
from app import socketio
from flask_socketio import send,emit
from datetime import datetime



@socketio.on('my broadcast event')
def test_message(message):
    print(message)
    user=UserTable.query.filter_by(username=message['username']).first()
    group=GroupTable.query.filter_by(id=message['groupidnumber']).first()
    messageobj=Message()
    messageobj.message=message['message']
    messageobj.group_id=group.id
    messageobj.user_id=user.id
    messageobj.user_name=user.username
    db.session.add(messageobj)
    db.session.commit()
    emit(str(message['groupidnumber']), {'message': message['message'],'username': message['username'],'groupidnumber':message['groupidnumber'],'time':message['time']}, broadcast=True)

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))