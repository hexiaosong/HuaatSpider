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
)