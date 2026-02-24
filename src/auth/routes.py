from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

from src.extensions import db
from src.auth.models import User
from src.auth.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth',__name__,url_prefix='/auth')

@auth_bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # home

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address is already registered.','danger')
            return redirect(url_for('auth.register'))
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data,password_hash=hashed_pw)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_locked:
            flash('Account locked due to too many failed attempts.','danger')
            return redirect(url_for('auth.login'))
        if user and check_password_hash(user.password_hash,form.password.data):
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            user.failed_login_attempts = 0
            db.session.commit()
            flash('Welcome back!','success')
            return redirect(url_for('auth.login'))
        else:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.is_locked = True
                db.session.commit()
            flash('Invalid email or password','danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
