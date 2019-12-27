from app.main import bp
from flask import render_template,url_for,flash,request,redirect, jsonify, send_from_directory
from app import db
from app.models import UserTable,GroupTable,Message, GroupMembers
from flask_login import current_user
from app import socketio
from flask_socketio import send,emit
from datetime import datetime
from app.services import is_authenticated
from flask import g
from app.dashboard.forms import SearchForm
from app.services import get_list_of_group_id
from app.search import add_to_index,query_index, remove_from_index
from random import randint
from app import celery
import pdfkit
import os
# from celery import AsyncResult
from app import app


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
    messages,total_message=query_index('message',g.search_form.q.data,1,5)
    users,total_users=query_index('user_table',g.search_form.q.data,1,5)
    current_user_group_id=get_list_of_group_id()
    print(groups)
    print(current_user_group_id)
    groups_searched=[]
    for group in groups:
        if(group in current_user_group_id):
            groups_searched.append(GroupTable.query.filter_by(id=group).first())
    users_searched=[]
    for user in users:
        users_searched.append(UserTable.query.filter_by(id=user).first())
    message_searched=[]
    for message in messages:
        if(Message.query.filter_by(id=message).first().user_id ==  current_user.id):
            message_searched.append(Message.query.filter_by(id=message).first())
    return render_template('search.html',title='Search',users=users_searched,groups=groups_searched,messages=message_searched)






@celery.task()
def download_chat(groupid,user_id):
    with app.app_context():
        print(os.getcwd())
        group = GroupTable.query.filter_by(id=groupid).first()
        user=UserTable.query.filter_by(id=user_id).first()
        if(GroupMembers.query.filter_by(group_id=group.id, member_id=user.id).order_by(Message.message_time.desc())):
            messages = Message.query.filter_by(group_id=group.id).order_by(
                Message.message_time.desc()).all()
            output =  render_template('message_pdf.html', username=user.username, title=group.groupname, messages=messages, groupname=group.groupname, groupdescription=group.group_description, groupid=groupid)
        randnum=str(randint(1,9999999999999999999))
        randpath='temp/'+randnum+'.html'
        f=open(randpath,'w')
        f.write(output)
        f.close()
        pdf=pdfkit.from_file(randpath,'temp/'+randnum+'.pdf')
        if os.path.exists(randpath):
            os.remove(randpath)
        return randnum


@bp.route('/download_content/<task_id>/<group_id>')
def download_content(group_id,task_id):
    if not(is_authenticated()):
        return 'Not Logged In'
    if not(GroupTable.query.filter_by(id=group_id).first().admin_id==current_user.id):
        return 'Unauthorised Action'
    download_object=download_chat.apply_async(args=[group_id,current_user.id])
    print(download_object.id)
    return download_object.task_id

@bp.route('/download/<task_id>')
def download(task_id):
    if not(is_authenticated()):
        return 'Not Logged In'
    print('_________________')
    res = download_chat.AsyncResult(task_id=task_id)
    print(res)
    print('_________________')
    print(res.status)
    if(res.status=='PENDING'):
        return 'wait'
    if(res.status == 'SUCCESS'):
        return res.result
        return send_from_directory(directory='temp', filename=res.result+'.pdf')