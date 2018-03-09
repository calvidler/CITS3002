from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    # Fields for logging into the website
    username = StringField('Username', [validators.Length(min=3, max=25), DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    # Form for registering a user
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')


class TransactionForm(FlaskForm):
    # Form for submitting a transaction
    to_user = SelectField('Send to')
    amount = IntegerField('Chriscoin Amount')
    submit = SubmitField('Submit')

