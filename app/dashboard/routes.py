from flask import render_template,url_for,flash,request,redirect
from flask_login import current_user
from app import db
from app.dashboard import bp
from app.models import UserTable,GroupTable,GroupMembers,Message
from app.dashboard.forms import MessageForm, CreateGroup, AddMembers, ChangeGroupDescription
from flask_socketio import send,emit
from app.services import is_authenticated, get_list_of_groups, get_current_user,create_new_group, get_group, create_message, get_group_single, get_group_members_names, get_group_members, leave_group, add_group_members, change_group_description, delete_group, remove_group_member

@bp.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if is_authenticated():
        groups,username=get_list_of_groups()
        return render_template('dashboard/dashboard.html',groups=groups,username=username)
    else:
        flash('Sorry, you are not logged in. Please login to continue.')
        return redirect(url_for('auth.login'))

@bp.route('/group/<groupid>',methods=['GET','POST'])
def group(groupid):
    if not(is_authenticated()):
        flash('Sorry, you are not logged in. Please login to continue')
        return redirect(url_for('auth.login'))
    if not(GroupMembers.query.filter_by(member_id=current_user.id).filter_by(group_id=groupid).all()):
        return render_template('errors/404.html'), 404
    user=get_current_user()
    group=get_group(groupid)
    if not(group):
        return render_template('errors/404.html'), 404
    page = request.args.get('page', 1, type=int)
    group=GroupTable.query.filter_by(id=groupid).first()
    if(GroupMembers.query.filter_by(group_id=group.id,member_id=user.id).order_by(Message.message_time.desc())):
        messages=Message.query.filter_by(group_id=group.id).order_by(Message.message_time.desc()).paginate(page,3,False)
        form=MessageForm()
        if form.validate_on_submit():
            create_message(form)
        next_url = url_for('dashboard.group', page=messages.next_num,groupid=groupid) \
        if messages.has_next else None
        prev_url = url_for('dashboard.group', page=messages.prev_num,groupid=groupid) \
        if messages.has_prev else None
        return render_template('dashboard/messages.html',group=group.id,username=user.username,title=group.groupname,messages=messages.items,form=MessageForm(),groupname=group.groupname,groupdescription=group.group_description,groupid=groupid,next_url=next_url,prev_url=prev_url)
    else:
        flash('Sorry, this group is not found')
        return redirect(url_for('auth.login'))

@bp.route('/creategroup',methods=['GET','POST'])
def creategroup():
    if not(current_user.is_authenticated):
        flash('Sorry, you are not logged in. Please login to continue.')
        return redirect(url_for('auth.login'))
    form=CreateGroup()
    if form.validate_on_submit():
        create_group_bool=create_new_group(form)
        if(create_group_bool):
            flash('Group created successful')
            return redirect(url_for('dashboard.dashboard'))
    return render_template('dashboard/creategroup.html',form=form)

                
@bp.route('/group/<group_id>/groupinfo',methods=['POST','GET'])
def groupinfo(group_id):
    if not(is_authenticated()):
        flash('Sorry, you are not logged in. Please login to continue')
        return redirect(url_for('auth.login'))
    if not(GroupMembers.query.filter_by(member_id=current_user.id).filter_by(group_id=group_id).all()):
        return render_template('errors/404.html'), 404
    user=get_current_user()
    group=get_group_single(group_id)
    members=get_group_members(group_id)
    members_names=get_group_members_names(members)
    admin=UserTable.query.filter_by(id=group.admin_id).first()
    form=AddMembers()
    description_form=ChangeGroupDescription()
    if description_form.validate_on_submit():
        change_group_description(description_form,group_id)
        redirect(url_for('dashboard.groupinfo',group_id=group_id))
    if form.validate_on_submit():
        add_group_members(form,group_id)
        return redirect(url_for('dashboard.groupinfo',group_id=group_id))
    if(admin.id!=user.id):
        return render_template('dashboard/showmembers.html',currentid=current_user.id,groupid=group_id,members=members_names,group=group.groupname,description=group.group_description,admin=admin.username,is_admin=False,form=form,changedesc=description_form)
    else:
        return render_template('dashboard/showmembers.html',currentid=current_user.id,groupid=group_id,members=members_names,group=group.groupname,description=group.group_description,admin='You are the admin',is_admin=True,form=form,changedesc=description_form)


@bp.route('/leavegroup/<groupid>',methods=['POST','GET'])
def leavegroup(groupid):
    if(GroupTable.query.filter_by(id=groupid).first().admin_id==current_user.id):
        flash("You can't leave group in which you are the admin. You can delete the group itself.")
        return redirect(url_for('dashboard.dashboard'))
    groupname=leave_group(groupid)
    flash('You left the group "'+groupname+'"')
    return redirect(url_for('dashboard.dashboard'))

@bp.route('/deletegroup/<groupid>',methods=['POST','GET'])
def deletegroup(groupid):
    if(GroupTable.query.filter_by(id=groupid).first().admin_id !=current_user.id):
        flash('Unauthorised action')
        return redirect(url_for('dashboard.dashboard'))
    groupname=delete_group(groupid)
    flash('You deleted the group "'+groupname+'"')
    return redirect(url_for('dashboard.dashboard'))

@bp.route('/removemember/<groupid>/<memberid>',methods=['POST','GET'])
def removemember(groupid,memberid):
    if(GroupTable.query.filter_by(id=groupid).first().admin_id !=current_user.id):
        flash('Unauthorised action')
        return redirect(url_for('dashboard.dashboard'))
    groupmembername=remove_group_member(memberid,groupid)
    flash('You removed "'+groupmembername+'" from the group')
    return redirect(url_for('dashboard.groupinfo',group_id=groupid))

