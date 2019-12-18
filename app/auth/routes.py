from flask import render_template,url_for,flash,request,redirect
from flask_login import login_user,logout_user,current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import UserTable

@bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=LoginForm()
    if form.validate_on_submit():
        user=UserTable.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Wrong username or password')
            return redirect(url_for('auth.login'))
        else:
            login_user(user,remember=form.remember_me.data)
            return render_template('base.html')
    return render_template('auth/login.html',title='Login',form=form)

@bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegisterForm()
    if form.validate_on_submit():
        user=UserTable(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login to continue')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',title='Register',form=form)

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Logout successful')
        return redirect(url_for('auth.login'))
    return redirect(url_for('auth.login'))