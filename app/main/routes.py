from app.main import bp
from flask import render_template,url_for,flash,request,redirect
from app import db
from app.models import UserTable,GroupTable,Message
from flask_login import current_user
from app import socketio
from flask_socketio import send,emit
from datetime import datetime
from app.services import is_authenticated
from flask import g
from app.dashboard.forms import SearchForm
from app.services import get_list_of_group_id
from app.search import add_to_index,query_index, remove_from_index


@socketio.on('messagetoserver')
def message_from_client(message):
    if not(is_authenticated()):
        return redirect(url_for('auth.login'))
    user=UserTable.query.filter_by(id=current_user.id).first()
    group=GroupTable.query.filter_by(id=message['groupidnumber']).first()
    messageobj=Message(message=message['message'],group_id=group.id,user_id=current_user.id,user_name=user.username)
    db.session.add(messageobj)
    db.session.commit()
    add_to_index('message',messageobj)
    emit(str(message['groupidnumber']), message, broadcast=True)


@bp.route('/')
@bp.route('/index')
def index():
    if is_authenticated():
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

@bp.before_app_request
def before_request():
    if is_authenticated():
        g.search_form=SearchForm()

@bp.route('/search')
def search():
    if not(is_authenticated()):
        flash('Sorry you are not logged in. Login to continue')
        return redirect(url_for('auth.login'))
    if not g.search_form.validate():
        return redirect(url_for('main.dashboard'))
    groups,total_groups=query_index('group_table',g.search_form.q.data,1,5)
    message,total_groups=query_index('message',g.search_form.q.data,1,5)
    users,total_users=query_index('user_table',g.search_form.q.data,1,5)
    message=message.filter_by(user_id=current_user.id)
    current_user_group_id=get_list_of_group_id()
    print(groups.all())
    groups_searched_for=[]
    for group in groups:
        if group.id in current_user_group_id:
            groups_searched_for.append(group)
    print(groups_searched_for)
    print(users.all())
    print(message.all())
    return 'helloworld'
    #return render_template('search.html',title='Search',users=users,groups=groups,message=message)