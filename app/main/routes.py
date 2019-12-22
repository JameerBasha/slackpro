from app.main import bp
from flask import render_template,url_for,flash,request,redirect
from app import db
from app.models import UserTable,GroupTable,Message
from flask_login import current_user
from app import socketio
from flask_socketio import send,emit
from datetime import datetime
from app.services import db_committer, is_authenticated



@socketio.on('messagetoserver')
def test_message(message):
    if not(is_authenticated()):
        flash('Sorry you are not logged in. Please login to continue')
        return redirect(url_for('auth.login'))
    user=UserTable.query.filter_by(username=message['username']).first()
    group=GroupTable.query.filter_by(id=message['groupidnumber']).first()
    messageobj=Message(message=message['message'],group_id=group.id,user_id=user.id,user_name=user.username)
    db_committer(messageobj)
    emit(str(message['groupidnumber']), message, broadcast=True)


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))