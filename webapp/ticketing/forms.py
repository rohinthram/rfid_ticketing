from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ticketing.models import User

from string import *
from datetime import datetime

class SignUpForm(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    username = StringField('User Name', validators=[DataRequired(), Length(min=3, max=20)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    mobile = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    tag_id = StringField('Tag ID', validators=[DataRequired(), Length(min=8, max=8)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=7)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The Username is Already taken')
        else:
            for i in username.data:
                print(i)
                if i not in ascii_letters+digits:
                    raise ValidationError('Username should contain only Alphanumeric characters')    

    def validate_email(self, email):
        user = User.query.filter_by(mail=email.data).first()
        if user:
            raise ValidationError('Account already exists')

    def validate_mobile(self, mobile):
        try:
            n = int(mobile.data)
        except:
            raise ValidationError('Invalid Mobile Number')
    
    def validate_dob(self, dob):
        d = datetime.now().strftime('%Y-%m-%d')
        #yr = int(datetime.now().strftime('%Y')) 
        # threshold for account creation can be added
        if str(dob.data) >= d:
            raise ValidationError('Invalid DOB')


class LoginForm(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class ForgetPasswordForm(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    submit = SubmitField('Get Reset Link')
    def validate_email(self, email):
        user = User.query.filter_by(mail=email.data).first()
        if not user:
            raise ValidationError('No such account exists')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])
    submit = SubmitField('Reset Password')
