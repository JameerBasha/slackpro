from flask import render_template,url_for,flash,request,redirect
from flask_login import current_user
from app import db
from app.dashboard import bp
from app.models import UserTable,GroupTable,GroupMembers,Message
from app.dashboard.forms import MessageForm, CreateGroup, AddMembers
from flask_socketio import send,emit

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

    page = request.args.get('page', 1, type=int)

    if(GroupMembers.query.filter_by(group_id=group.id,member_id=user.id).order_by(Message.message_time.desc())):
        messages=Message.query.filter_by(group_id=group.id).order_by(Message.message_time.desc()).paginate(page,3,False)
        form=MessageForm()
        if form.validate_on_submit():
            messageobj=Message()
            messageobj.message=form.message.data
            messageobj.group_id=group.id
            messageobj.user_id=user.id
            messageobj.user_name=user.username
            db.session.add(messageobj)
            db.session.commit()


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
        flash('Group created successful')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('dashboard/creategroup.html',form=form)

                
@bp.route('/group/<group_id>/groupinfo',methods=['POST','GET'])
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
    if form.validate_on_submit():
        group_members=form.members.data.split(',')
        print(group_members )
        for members in group_members:
            if (UserTable.query.filter_by(username=members).first()):
                if (GroupMembers.query.filter_by(member_name=members).filter_by(group_id=group.id).first()):
                    print('))))))))))))))))))))))))))))))0')
                    continue
                print('__________________________')
                temp_group_members=GroupMembers()
                temp_member=UserTable.query.filter_by(username=members).first()
                temp_group_members.member_id=temp_member.id
                temp_group_members.member_name=temp_member.username
                temp_group_members.group_id=group_id
                db.session.add(temp_group_members)
                db.session.commit()
                return redirect(url_for('dashboard.groupinfo',group_id=group_id))
    if(admin.id!=user.id):
        return render_template('dashboard/showmembers.html',currentid=current_user.id,groupid=group_id,members=members_names,group=group.groupname,description=group.group_description,admin=admin.username,is_admin=False,form=form)
    else:
        return render_template('dashboard/showmembers.html',currentid=current_user.id,groupid=group_id,members=members_names,group=group.groupname,description=group.group_description,admin='You are the admin',is_admin=True,form=form)


@bp.route('/leavegroup/<groupid>',methods=['POST','GET'])
def leavegroup(groupid):
    if(GroupTable.query.filter_by(id=groupid).first().admin_id==current_user.id):
        flash("You can't leave group in which you are the admin. You can delete the group itself.")
        return redirect(url_for('dashboard.dashboard'))
    groupname=GroupTable.query.filter_by(id=groupid).first().groupname
    GroupMembers.query.filter_by(member_id=current_user.id).filter_by(group_id=groupid).delete()
    db.session.commit()
    flash('You left the group "'+groupname+'"')
    return redirect(url_for('dashboard.dashboard'))

@bp.route('/deletegroup/<groupid>',methods=['POST','GET'])
def deletegroup(groupid):
    if(GroupTable.query.filter_by(id=groupid).first().admin_id !=current_user.id):
        flash('Unauthorised action')
        return redirect(url_for('dashboard.dashboard'))
    groupname=GroupTable.query.filter_by(id=groupid).first().groupname
    GroupMembers.query.filter_by(group_id=groupid).delete()
    Message.query.filter_by(group_id=groupid).delete()
    GroupTable.query.filter_by(id=groupid).delete()
    db.session.commit()
    flash('You deleted the group "'+groupname+'"')
    return redirect(url_for('dashboard.dashboard'))

@bp.route('/removemember/<groupid>/<memberid>',methods=['POST','GET'])
def removemember(groupid,memberid):
    if(GroupTable.query.filter_by(id=groupid).first().admin_id !=current_user.id):
        flash('Unauthorised action')
        return redirect(url_for('dashboard.dashboard'))
    groupmembername=GroupMembers.query.filter_by(member_id=memberid).filter_by(group_id=groupid).first().member_name
    GroupMembers.query.filter_by(member_id=memberid).filter_by(group_id=groupid).delete()
    db.session.commit()
    flash('You removed "'+groupmembername+'" from the group')
    return redirect(url_for('dashboard.groupinfo',group_id=groupid))

