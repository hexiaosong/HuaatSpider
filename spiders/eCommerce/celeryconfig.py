# coding:utf-8
from kombu import Exchange, Queue

CELERY_IMPORTS = ('JDSpider',
                  'GomeSpider',
                  'SuningSpider',
                  )

config = {
    'CELERY_QUEUES': [
        Queue('jd_spider', exchange=Exchange('spider'), routing_key='app.jd_spider'),
        Queue('gome_spider', exchange=Exchange('spider'), routing_key='app.gome_spider'),
        Queue('suning_spider', exchange=Exchange('spider'), routing_key='app.suning_spider'),
    ],
    'CELERY_ROUTES': {
        'jd_spider': {'queue': 'jd_spider'},
        'gome_spider': {'queue': 'gome_spider'},
        'suning_spider': {'queue': 'suning_spider'},
    },

    'CELERY_TIMEZONE': 'Asia/Chongqing',
    'CELERY_ENABLE_UTC' : True,
    'CELERY_ACCEPT_CONTENT': ['pickle', 'json', 'msgpack', 'yaml'],
    'CELERY_TASK_SERIALIZER' : 'json',
    'CELERY_RESULT_SERIALIZER' : 'json',
}