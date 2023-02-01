import psycopg2
from notification_api.config import DATABASE_HOST,DATABASE_PORT,DATABASE_NAME,DATABASE_USERNAME,DATABASE_PASSWORD

def getconnection():
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT)
    return conn    

