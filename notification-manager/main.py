
from notification_api import setup_app
from notification_api.io.redis_stream.reader import notification



if __name__ == '__main__':
    setup_app()
    notification.app()
