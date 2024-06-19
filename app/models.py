from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # otp_secret = db.Column(db.String(16))  # Add otp_secret column
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # def get_totp_uri(self):
    #     import pyotp
    #     return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
    #         name=self.username,
    #         issuer_name='FlaskApp'
    #     )

    # def verify_totp(self, token):
    #     import pyotp
    #     totp = pyotp.TOTP(self.otp_secret)
    #     return totp.verify(token)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    birth_date = db.Column(db.Date)
    parent_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    children = db.relationship('Person')

    def __repr__(self):
        return f'<Person {self.first_name} {self.last_name}>'