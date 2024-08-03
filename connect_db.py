from sqlalchemy import create_engine

def get_connection():
    # Replace with your actual MySQL database URI
    database_uri = 'mysql+pymysql://root:root@localhost:3306/chat'
    engine = create_engine(database_uri)
    return engine