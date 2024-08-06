from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    def __init__(self, username):
        self.username = username
    username = db.Column(db.String(80), unique=True, primary_key=True)
    FirstName = db.Column(db.String(80), nullable=False)
    LastName = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(90), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(300), nullable=False)
    actif = db.Column(db.Boolean, default=False)
    lang=db.Column(db.String(10), unique=False,default='en')
    img = db.Column(db.Text, nullable=True)

    messages_sent = db.relationship('Message', foreign_keys='Message.sender', backref='sender_user', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient', backref='recipient_user', lazy='dynamic')

    sent_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.user', backref='requester', lazy='dynamic')
    received_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.friend', backref='receiver', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    img = db.Column(db.Text, nullable=True)
    pdf = db.Column(db.Text, nullable=True)  # Consider storing URLs if using a storage service
    sender = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    recipient = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)

class Friendship(db.Model):
    __tablename__ = 'friendship'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    friend = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    accepted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
