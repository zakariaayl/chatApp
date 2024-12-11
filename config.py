import os
from datetime import timedelta
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '111'
user = 'root'
password = 'root'
host = '127.0.0.1'
port = 3306
database = 'chat'
SQLALCHEMY_DATABASE_URI ='mysql+pymysql://root:root@localhost:3306/chat'
# SQLALCHEMY_DATABASE_URI=f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '111'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
PERMANENT_SESSION_LIFETIME=timedelta(days=7)

