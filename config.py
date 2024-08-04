import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '111'
user = 'root'
password = 'root'
host = '127.0.0.1'
port = 3306
database = 'chat'
SQLALCHEMY_DATABASE_URI ='postgresql://zaki:v2zn20TKS7m18cK0PC2jm7E71CVXkCb6@dpg-cqn9c2tsvqrc73flkkeg-a.oregon-postgres.render.com/chat_gyiu'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '111'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
