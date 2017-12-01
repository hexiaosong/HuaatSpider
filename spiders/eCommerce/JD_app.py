from celery import Celery
from settings import MY_BROKER_URL,MY_CELERY_RESULT_BACKEND
from celeryconfig import *

app = Celery(
    broker = MY_BROKER_URL,
    backend = MY_CELERY_RESULT_BACKEND,
    include=['spiders.eCommerce.JDSpider']
)

app.config_from_object(config)



LAUNCHER_ARGV = 'celery worker -A spiders.eCommerce.JD_app -Q jd_spider -l info -c 3'.split()

if __name__ == '__main__':
    app.start(argv=LAUNCHER_ARGV)