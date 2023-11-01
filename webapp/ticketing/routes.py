from flask import render_template, request, url_for, flash, redirect
from ticketing import app, db, bcrypt
from ticketing.forms import SignUpForm, LoginForm, ForgetPasswordForm, ResetPasswordForm 
from ticketing.models import User, Bus, Transit
from flask_login import login_user, current_user, logout_user, login_required

from ticketing.models import Transit

import string
import random
import datetime

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        flash('Already Logged In.', 'info')
        return redirect(url_for('dashboard'))

    form = SignUpForm()

    if form.validate_on_submit(): 
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(tag_id=form.tag_id.data, username=form.username.data, password=hashed_password, mail=form.email.data, dob=form.dob.data, amt=0, history='', mobile=form.mobile.data, address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for { form.username.data } ! You can now log in', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form, title='Sign Up')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already Logged In.', 'info')
        return redirect(url_for('dashboard'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
            #next_page = request.args.get('next')
            #return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', form=form, title='Login')


###########################Sending Reset Password Mail################################
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import mimetypes

import os

def send_mail(to, subject, body, format='plain', attachments=[]):

    pwd = os.getcwd()
    os.chdir('/home/ticketing/mysite/ticketing')

    creds = None
    SCOPES = ['https://mail.google.com/']
    print(os.getcwd())
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    file_attachments = attachments

    #html = ''
    #with open('message.html') as msg:
    #    html += msg.read()

    #create email
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject
    #mimeMessage.attach(MIMEText(html,'html'))
    mimeMessage.attach(MIMEText(body, format))

    for attachment in file_attachments:
        content_type, encoding = mimetypes.guess_type(attachment)
        main_type, sub_type = content_type.split('/', 1)
        file_name = os.path.basename(attachment)

        with open(attachment, 'rb') as f:
            myFile = MIMEBase(main_type, sub_type)
            myFile.set_payload(f.read())
            myFile.add_header('Content-Disposition', attachment, filename=file_name)
            encoders.encode_base64(myFile)

        mimeMessage.attach(myFile)


    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()


    message = service.users().messages().send(
        userId='me',
        body={'raw': raw_string}).execute()

    os.chdir(pwd)
    return message


def send_reset_email(user):
    m = 5
    token = user.get_reset_token(m*60) #120 sec valid token
    subject = 'Password Reset Request'
    to = user.mail
    body = f'''
    To reset Password, Click on the following link (expires in {m} mins)
    {url_for('reset_password', token=token, _external=True)}
    '''
    send_mail(to, subject, body)



@app.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = ForgetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.email.data).first()
        send_reset_email(user)
        flash('Please check your mail for reset !', 'info')
        return redirect(url_for('login'))

    return render_template('password_reset.html', title='Forgot Password', form=form)

@app.route('/forget_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid request or Expired token !!!', 'warning')
        return redirect(url_for('forget_password'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset! ', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password',form=form)



'''
@app.route('/login-admin')
def login_admin():
    return 'hello'
'''


@app.route('/dashboard')
@login_required
def dashboard():
    txn = []
    for i in current_user.history.split(','):
        x = Transit.query.filter_by(id=i).first()
        txn.append(x)

    return render_template('dashboard.html', user=current_user, txn=txn, title=current_user.username)


@app.route('/load_money/<username>/<money>/<pswd>')
def load_money(username, money, pswd):

    if pswd != "123":
        return 'Auth Falied'

    user = User.query.filter_by(username=username).first()
    user.amt += int(money)
    db.session.commit()
    return 'Money Loaded !'

@app.route('/block-tag')
@login_required
def block_tag():
    user = User.query.filter_by(username=current_user.username).first()
    if user.is_blocked:
        user.is_blocked = False
        stmt = "Account Activated"
    else:
        user.is_blocked = True
        stmt = "Account Blocked"

    db.session.commit()
    return stmt

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully Logged Out!', 'success')

    return redirect(url_for('login'))


import json

def calculateFare(start, end, fare):
    f = abs(ord(end) - ord(start))
    f *= fare
    return f
  

@app.route('/update', methods=['POST'])
def update():
    req = request.data
    req = json.loads(req)
    tag_id = str(req['tag_id'])
    tag_id = tag_id.upper()
    req["bus_id"] = int(req["bus_id"])
    #return tag_id
    key = req['key']
    print("Tag ID : "+tag_id)
    if key != "123":
        return '{code:-1, err:Unauthorized Access}'

    user = User.query.filter_by(tag_id=tag_id).first()   

    if not user:
        return '0'

    bus = Bus.query.filter_by(id=req['bus_id']).first()
    if not bus:
        return 'Fatal Error'

    id = ''.join([random.choice(string.ascii_letters+string.digits) for i in range(10)])

    if user.on_board:
        id = user.history.split(',')[-1]
        transit = Transit.query.filter_by(id=id).first()
        
        fare = calculateFare(transit.b_in, bus.loc, bus.fare)
        transit.b_out_time = str(datetime.datetime.now())[:-7]
        transit.charge = fare
        user.amt -= fare
        if user.amt < -50:
            to = user.mail
            subject = "Low Balance"
            body = "Please load money!"
            send_mail(to, subject, body)
            user.is_blocked = True

        transit.b_out = bus.loc
        user.on_board = False
    
        db.session.commit()

        return '2' + 'Fare:' + str(fare) + ';Bal:' + str(user.amt)
    else:
        if user.amt <= -50:
            user.is_blocked = True 
            db.session.commit()

        if user.is_blocked:
            return '0'
        
        t_in = str(datetime.datetime.now())[:-7]
        transit = Transit(id=id, username=user.username, b_in_time=t_in, b_out_time=t_in, bus_no=req['bus_id'], b_in=bus.loc, b_out=bus.loc,charge=0)
        db.session.add(transit)

        if user.history:
            user.history += ','+id
        else:
            user.history = id
        user.on_board = True

        db.session.commit()
        return '1' + str(user.username)
        
    
@app.route('/add-bus/<fare>/<pswd>')
def add_bus(fare, pswd):
    if pswd != "123":
        return 'Hello'
        
    bus = Bus(loc='A', fare=fare)
    db.session.add(bus)
    db.session.commit()
    return "Bus Added"

@app.route('/update-bus-loc/<id>/<loc>/<pswd>')
def update_bus_loc(id, loc, pswd):
    if pswd != "123":
        return 'Hello'
    bus = Bus.query.filter_by(id=id).first()
    if not bus:
        return "Bus Not Found"
    
    if loc not in string.ascii_uppercase:
        return "Invalid To Location"

    bus.loc = loc
    db.session.commit()
    return "Location Updated !"