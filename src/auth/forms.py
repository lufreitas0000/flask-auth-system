from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    email = StringField('Email Address',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="email")
                        ])
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


class ResetPasswordForm(FlaskForm):
    """Form to submit a brand new password."""
    password = PasswordField('New Password',
                             validators=[
                                 DataRequired(message="Password is required.")
                             ])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[
                                         DataRequired(message="Please confirm your password."),
                                         EqualTo('password', message="Passwords must match.")
                                     ])
    submit = SubmitField('Reset Password')
