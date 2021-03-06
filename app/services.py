from app import db
from flask_login import current_user
from app.models import GroupMembers, UserTable, GroupTable, Message
from app.search import add_to_index,remove_from_index, query_index
from flask import current_app

def is_authenticated():
	if(current_user.is_authenticated):
		return True
	else:
		return False


def get_list_of_groups():
	user=UserTable.query.filter_by(username=current_user.username).first()
	groups_as_member=GroupMembers.query.filter_by(member_id=user.id).all()
	groups=[]
	for group in groups_as_member:
		temp_group=GroupTable.query.filter_by(id=group.group_id).first()
		if(temp_group):
			groups.append([temp_group.groupname,temp_group.id,temp_group.group_description])
	return groups,user.username

def get_list_of_group_id():
	user=UserTable.query.filter_by(username=current_user.username).first()
	groups_as_member=GroupMembers.query.filter_by(member_id=user.id).all()
	group_id=[]
	for group in groups_as_member:
		group_id.append(group.group_id)
	return group_id

def get_current_user():
	user=UserTable.query.filter_by(username=current_user.username).first()
	return user

def create_new_group(form):
	user=get_current_user()
	newgroup=GroupTable(admin_id=current_user.id,groupname=form.group_name.data,group_description=form.group_description.data)
	db.session.add(newgroup)
	db.session.commit()
	add_to_index('group_table',newgroup)
	group_members=form.group_members.data.split(',')
	if user.username not in group_members:
		group_members.append(user.username)
	for members in group_members:
	    if(UserTable.query.filter_by(username=members).first()):
	        temp_member=UserTable.query.filter_by(username=members).first()
	        temp_group_members=GroupMembers(member_id=temp_member.id,member_name=temp_member.username,group_id=newgroup.id)
	        db.session.add(temp_group_members)
	db.session.commit()
	return True

def get_group(group_id):
	group=GroupTable.query.filter_by(id=group_id).all()
	return group

def create_message(form,groupid,user):
	messageobj=Message(message=form.message.data,group_id=groupid,user_id=user.id,user_name=user.username)
	db.session.add(messageobj)
	db.session.commit()
	add_to_index('message',messageobj)
	return True

def get_group_single(group_id):
	group=GroupTable.query.filter_by(id=group_id).first()
	return group

def get_group_members(group_id):
	members=GroupMembers.query.filter_by(group_id=group_id).all()
	return members

def get_group_members_names(members):
	members_names=[]
	for member in members:
		members_names.append([member.member_name,UserTable.query.filter_by(id=member.member_id).first()])
	return members_names

def leave_group(group_id):
	groupname=GroupTable.query.filter_by(id=groupid).first().groupname
	GroupMembers.query.filter_by(member_id=current_user.id).filter_by(group_id=groupid).delete()
	db.session.commit()
	return groupname

def add_group_members(form,group_id):
	group_members=form.members.data.split(',')
	for members in group_members:
		if (UserTable.query.filter_by(username=members).first()):
			if (GroupMembers.query.filter_by(member_name=members).filter_by(group_id=group_id).first()):
				continue
			temp_member=UserTable.query.filter_by(username=members).first()
			temp_group_members=GroupMembers(member_id=temp_member.id,member_name=temp_member.username,group_id=group_id)
			db.session.add(temp_group_members)
			db.session.commit()

def change_group_description(form,group_id):
	GroupTable.query.filter_by(id=group_id).update({"group_description":form.description.data})
	db.session.commit()
	group_object=GroupTable.query.filter_by(id=group_id).first()
	add_to_index('group_table',group_object)

def delete_group(groupid):
	groupname=GroupTable.query.filter_by(id=groupid).first().groupname
	GroupMembers.query.filter_by(group_id=groupid).delete()
	messages=Message.query.filter_by(group_id=groupid).all()
	for message in messages:
		remove_from_index('message',message)
	Message.query.filter_by(group_id=groupid).delete()
	group=GroupTable.query.filter_by(id=groupid).first()
	remove_from_index('group_table',group)
	GroupTable.query.filter_by(id=groupid).delete()
	db.session.commit()
	return groupname

def remove_group_member(memberid,groupid):
	groupmembername=GroupMembers.query.filter_by(member_id=memberid).filter_by(group_id=groupid).first().member_name
	GroupMembers.query.filter_by(member_id=memberid).filter_by(group_id=groupid).delete()
	db.session.commit()
	return groupmembername