from celery import Celery
from settings import MY_BROKER_URL,MY_CELERY_RESULT_BACKEND
from celeryconfig import *

app = Celery(
    broker = MY_BROKER_URL,
    backend = MY_CELERY_RESULT_BACKEND,
    include=['spiders.eCommerce.JDSpider',
             'spiders.eCommerce.GomeSpider',
             'spiders.eCommerce.SuningSpider',
             ]
)

app.config_from_object(config)



JD_LAUNCHER_ARGV = 'celery worker -A spiders.eCommerce.app -Q jd_spider -l info -c 1'.split()
GOME_LAUNCHER_ARGV = 'celery worker -A spiders.eCommerce.app -Q gome_spider -l info -c 1'.split()
SUNING_LAUNCHER_ARGV = 'celery worker -A spiders.eCommerce.app -Q suning_spider -l info -c 1'.split()


if __name__ == '__main__':
    app.start(argv=SUNING_LAUNCHER_ARGV)