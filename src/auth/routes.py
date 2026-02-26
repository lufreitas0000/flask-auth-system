from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta

from src.extensions import db
from src.auth.models import User, AuditLog
from src.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm

auth_bp = Blueprint('auth',__name__,url_prefix='/auth')

@auth_bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # home

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address is already registered.','danger')
            return redirect(url_for('auth.register'))

        # Replace the db.session.add block with this:
        try:
            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, password_hash=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback() # Concern #2: Unbounded Transaction Fix
            flash('An error occurred while creating your account.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html',form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Lockout check
        if user and user.is_locked:
            if user.locked_until:
                # FIX: SQLite strips timezones. Add UTC back if it is missing!
                lock_expiration = user.locked_until
                if lock_expiration.tzinfo is None:
                    lock_expiration = lock_expiration.replace(tzinfo=timezone.utc)

                if datetime.now(timezone.utc) < lock_expiration:
                    # Still locked! Calculate remaining minutes
                    time_left = lock_expiration - datetime.now(timezone.utc)
                    minutes = int(time_left.total_seconds() // 60) + 1
                    flash(f'Account locked. Try again in {minutes} minutes.', 'danger')
                    return redirect(url_for('auth.login'))
                else:
                    # unlock account
                    user.is_locked = False
                    user.failed_login_attempts = 0
                    user.locked_until = None
                    db.session.commit()


        # Password check
        if user and check_password_hash(user.password_hash,form.password.data):
            try:
                user.last_login = datetime.now(timezone.utc)
                user.failed_login_attempts = 0

                log = AuditLog(
                    user_id = user.id,
                    ip_address = request.remote_addr,
                    was_successful = True
                )
                db.session.add(log)
                db.session.commit()

                login_user(user)
                flash('Welcome back!','success')
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred during login.','danger')
        else:
            if user:
                try:
                    # tell the SQL engine to do the math at the row level
                    user.failed_login_attempts = User.failed_login_attempts + 1
                    db.session.commit() # Execute the math in SQL
                    db.session.refresh(user)

                    max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
                    lockout_duration = current_app.config.get('LOCKOUT_DURATION_MINUTES', 15)
                    if user.failed_login_attempts >= max_attempts:
                        user.is_locked = True
                        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_duration)

                    log = AuditLog(
                        user_id = user.id,
                        ip_address = request.remote_addr,
                        was_successful = False
                    )
                    db.session.add(log)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
            flash('Invalid email or password.','danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password',methods=['GET','POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user : User | None = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_token()
            # We haven't installed Flask-Mail yet, so we will just print it to the server console for now!
            current_app.logger.info(f"MOCK EMAIL: Send reset link to {user.email} -> /reset_password/{token}")

        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/request_reset.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    user: User | None = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.request_reset'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password_hash = hashed_password

        user.is_locked = False
        user.failed_login_attempts = 0
        user.locked_until = None

        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_token.html', title='Reset Password', form=form)
