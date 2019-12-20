from flask import render_template,url_for,flash,request,redirect
from flask_login import current_user
from app import db
from app.dashboard import bp
from app.models import UserTable,GroupTable,GroupMembers,Message
from app.dashboard.forms import MessageForm, CreateGroup, AddMembers

@bp.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if current_user.is_authenticated:
        user=UserTable.query.filter_by(username=current_user.username).first()
        groups_as_member=GroupMembers.query.filter_by(member_id=user.id).all()
        groups=[]
        for group in groups_as_member:
            temp_group=GroupTable.query.filter_by(id=group.group_id).first()
            groups.append([temp_group.groupname,temp_group.id,temp_group.group_description])
        return render_template('dashboard/dashboard.html',groups=groups)
    else:
        flash('Sorry, you are not logged in. Please login to continue.')
        return redirect(url_for('auth.login'))

@bp.route('/group/<groupid>',methods=['GET','POST'])
def group(groupid):
    if not(current_user.is_authenticated):
        flash('Sorry, you are not logged in. Please login to continue')
        return redirect(url_for('auth.login'))
    user=UserTable.query.filter_by(username=current_user.username).first()
    group=GroupTable.query.filter_by(id=groupid).first()
    if(GroupMembers.query.filter_by(group_id=group.id,member_id=user.id).order_by(Message.message_time.desc())):
        messages=Message.query.filter_by(group_id=group.id).order_by(Message.message_time.desc())
        form=MessageForm()
        if form.validate_on_submit():
            messageobj=Message()
            messageobj.message=form.message.data
            messageobj.group_id=group.id
            messageobj.user_id=user.id
            messageobj.user_name=user.username
            db.session.add(messageobj)
            db.session.commit()
        return render_template('dashboard/messages.html',messages=messages,form=MessageForm(),groupname=group.groupname,groupdescription=group.group_description,groupid=groupid)
    else:
        flash('Sorry, this group is not found')
        return redirect(url_for('auth.login'))
    return render_template('base.html')

@bp.route('/creategroup',methods=['GET','POST'])
def creategroup():
    if not(current_user.is_authenticated):
        flash('Sorry, you are not logged in. Please login to continue.')
        return redirect(url_for('auth.login'))
    user=UserTable.query.filter_by(username=current_user.username).first()
    form=CreateGroup()
    if form.validate_on_submit():
        newgroup=GroupTable()
        newgroup.admin_id=user.id
        newgroup.groupname=form.group_name.data
        newgroup.group_description=form.group_description.data
        db.session.add(newgroup)
        db.session.commit()
        group_admin=GroupMembers()
        group_admin.member_name=user.username
        group_admin.member_id=user.id
        group_admin.group_id=newgroup.id
        db.session.add(group_admin)
        db.session.commit()
        group_members=form.group_members.data.split(',')
        for members in group_members:
            if(UserTable.query.filter_by(username=members).first()):
                temp_group_members=GroupMembers()
                temp_member=UserTable.query.filter_by(username=members).first()
                temp_group_members.member_id=temp_member.id
                temp_group_members.member_name=temp_member.username
                temp_group_members.group_id=newgroup.id
                db.session.add(temp_group_members)
                db.session.commit()
    return render_template('dashboard/creategroup.html',form=form)

                
@bp.route('/group/<group_id>/groupinfo')
def groupinfo(group_id):
    if not(current_user.is_authenticated):
        flash('Sorry, you are not logged in. Please login to continue')
        return redirect(url_for('auth.login'))
    user=UserTable.query.filter_by(username=current_user.username).first()
    group=GroupTable.query.filter_by(id=group_id).first()
    members=GroupMembers.query.filter_by(group_id=group_id).all()
    members_names=[]
    for member in members:
        members_names.append([member.member_name,UserTable.query.filter_by(id=member.member_id).first()])
    admin=UserTable.query.filter_by(id=group.admin_id).first()
    print(admin)
    form=AddMembers()
    if(admin.id!=user.id):
        return render_template('dashboard/showmembers.html',members=members_names,group=group.groupname,description=group.group_description,admin=admin.username,is_admin=False,form=form)
    else:
        return render_template('dashboard/showmembers.html',members=members_names,group=group.groupname,description=group.group_description,admin='You are the admin',is_admin=True,form=form)
