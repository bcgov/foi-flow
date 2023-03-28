from walrus import Database
from config import REDIS_HOST,REDIS_PORT,REDIS_PASSWORD

streamdb =  Database(host=str(REDIS_HOST), port=str(REDIS_PORT), db=0,password=str(REDIS_PASSWORD))
