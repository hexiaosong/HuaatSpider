# coding: utf-8
"""
Create on 2017/10/5

@author:hexiaosong
"""
import socket


HOSTNAME = socket.gethostname()

MONGODB_DATABASES = dict(
    # 主库
    main_mongo_db={
        'alias': 'HuaatSpiders',
        'name': 'HuaatSpiders',
        'username': '',
        'host': 'localhost',
        'password': '',
        'port': 27017,
        'connect': False,
    },
    aliyun_mongo_db={
        'alias': 'default',
        'name': 'HuaatSpiders',
        'username': 'test',
        'host': '118.190.150.207',
        'password': 'test123',
        'port': 27017,
        'connect': False,
    },
)

# REDIS_CACHE_URL = 'redis://118.190.150.207:6379/5'
REDIS_CACHE_URL = 'redis://localhost:6379/7'
MY_BROKER_URL = 'redis://:huaat666888@118.190.150.207:6379/10'
MY_CELERY_RESULT_BACKEND = 'redis://:huaat666888@118.190.150.207:6379/11'