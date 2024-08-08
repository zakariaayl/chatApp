from sqlalchemy import create_engine
import config
from sqlalchemy.exc import SQLAlchemyError
try:
    def get_connection():
    # Replace with your actual MySQL database URI
    database_uri =config.SQLALCHEMY_DATABASE_URI
    # 'postgresql://zaki:v2zn20TKS7m18cK0PC2jm7E71CVXkCb6@dpg-cqn9c2tsvqrc73flkkeg-a.oregon-postgres.render.com/chat_gyiu'
    engine = create_engine(database_uri)
    return engine
except SQLAlchemyError as e:
    print(f"An error occurred: {e}")