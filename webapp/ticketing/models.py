from ticketing import db, login_manager, app
from flask_login import UserMixin
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    mail = db.Column(db.String(40), unique=True, nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    amt = db.Column(db.Integer)
    history = db.Column(db.String(11*5))
    on_board = db.Column(db.Boolean, default=False, nullable=False)
    mobile = db.Column(db.String(10))
    address = db.Column(db.String(100), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)

    def get_reset_token(self, expiry_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expiry_sec)
        return s.dumps( {'user_id': self.id} ).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)

    def __repr__(self):
        return str(self.username) + ',' + str(self.is_blocked) + ',' + str(self.on_board) + ','  + str(self.amt)

'''
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    mail = db.Column(db.String(40), unique=True, nullable=False)
    acc_created = db.Column(db.String(100*20), unique=True, nullable=False)
'''

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loc = db.Column(db.String(1), nullable=False)
    fare = db.Column(db.Integer, nullable=False, default=0)


class Transit(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    b_in_time = db.Column(db.String(19), nullable=False)
    b_in = db.Column(db.String(20), nullable=False)
    b_out_time = db.Column(db.String(19), nullable=False)
    b_out = db.Column(db.String(20), nullable=False)
    bus_no = db.Column(db.Integer, nullable=False)
    charge = db.Column(db.Integer, nullable=False)

if "database.db" not in os.listdir():
    db.create_all()