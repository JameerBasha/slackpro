from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import UserTable
from flask import request

class MessageForm(FlaskForm):
    message=StringField('Write your message',validators=[DataRequired()])
    submit=SubmitField('Send')

class CreateGroup(FlaskForm):
    group_name=StringField('Group Name',validators=[DataRequired()])
    group_description=StringField('Description')
    group_members=StringField('Username of Members separated by commas ')
    submit=SubmitField('Create Group')

class AddMembers(FlaskForm):
    members=StringField('Members to add separated by commas',validators=[DataRequired()])
    submit=SubmitField('Add members')

class ChangeGroupDescription(FlaskForm):
    description=StringField('New group description',validators=[DataRequired()])
    submit=SubmitField('Change Group Description')

class SearchForm(FlaskForm):
    q=StringField('Search',validators=[DataRequired()])

    def __init__(self,*args,**kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata']=request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled']=False
        super(SearchForm,self).__init__(*args,**kwargs)