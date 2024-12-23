from walrus import Database
from config import REDIS_HOST,REDIS_PORT,REDIS_PASSWORD, REDIS_HEALTH_CHECK_INTERVAL

#streamdb =  Database(host=str(REDIS_HOST), port=str(REDIS_PORT), db=0,password=str(REDIS_PASSWORD))
print(REDIS_HOST)
streamdb =  Database(host=str(REDIS_HOST), port=str(REDIS_PORT), db=0,password=str(REDIS_PASSWORD), retry_on_timeout=True, health_check_interval=int(REDIS_HEALTH_CHECK_INTERVAL), socket_keepalive=True)
