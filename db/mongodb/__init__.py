# coding: utf-8
"""
Create on 2017/10/2

@author:hexiaosong
"""


from mongoengine import register_connection

from settings.settings_local import MONGODB_DATABASES

# 注册数据库连接
for name, data in MONGODB_DATABASES.items():
    register_connection(**data)