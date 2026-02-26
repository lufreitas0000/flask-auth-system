from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from src.auth.models import User

class PasswordBaseForm(FlaskForm):
    """A base form that provides standard password and confirmation fields."""
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(message="Password is required."),
                                 Length(min=8, message="Password must be at least 8 characters long.")
                             ])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[
                                         DataRequired(message="Please confirm your password."),
                                         EqualTo('password', message="Passwords must match.")
                                     ])

class RegistrationForm(PasswordBaseForm):
    email = StringField('Email Address',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="Please enter a valid email address.")
                        ])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email address is already registered. Please log in.')

    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    email = StringField('Email Address',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="Please enter a valid email address.")
                        ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(message="Password is required.")
                             ])

    submit = SubmitField('Log In')

class RequestResetForm(FlaskForm):
    """Form for users to request a password reset link."""
    email = StringField('Email Address',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="Please enter a valid email address.")
                        ])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(PasswordBaseForm):
    """Form to submit a brand new password."""
    submit = SubmitField('Reset Password')
