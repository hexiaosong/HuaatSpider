# coding: utf-8
"""
Create on 2017/10/3

@author:hexiaosong
"""

from settings_local import *
from settings import *
from bson import json_util as json

for name, data in MONGODB_DATABASES.items():
    data_fix = dict(data)
    print(json.dumps(data_fix, indent=4))

if MY_BROKER_URL:
    print MY_BROKER_URL
if MY_CELERY_RESULT_BACKEND:
    print MY_CELERY_RESULT_BACKEND