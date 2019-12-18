from app.main import bp
from flask import render_template,url_for,flash,request,redirect
from app import db
from app.models import UserTable
from flask_login import current_user


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('base.html')
    return redirect(url_for('auth.login'))