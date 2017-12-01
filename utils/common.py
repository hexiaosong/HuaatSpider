# coding: utf-8
"""
Create on 2017/10/2

@author:hexiaosong
"""

import time
import re
import datetime
import requests
import redis
import urlparse
from bson import json_util
from settings.settings_local import REDIS_CACHE_URL


def time_deco(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        delta_time = end_time - start_time
        print('%s costs time : %f s' % (func.__name__, delta_time))
    return wrapper


def jprint(json_data):

    s = json_util.dumps(json_data, ensure_ascii=False, indent=4)
    print(s)

    return s


def yesterday_date():
    """获取昨天日期"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y_%m_%d')

    return yesterday_str


def test_proxy(host=None,port=None, is_proxy=False):
    start = time.time()
    if is_proxy:
        proxies = { "http": "http://%s:%s" % (host,port),}
        rsp = requests.get("http://www.ip168.com/json.do?view=myipaddress", proxies=proxies, timeout=10)
    else:
        rsp = requests.get("http://www.ip168.com/json.do?view=myipaddress",timeout=10)
    m = re.search('\[(.*)\]', rsp.text)
    if m:
        address = m.group(1)
        print(address)
    else:
        print('no response')
    end = time.time()
    print('Costs time %f' % (end-start))


def connect_redis(uri):
    puri = urlparse.urlparse(uri)
    host = puri.hostname
    port = puri.port
    password = puri.password if puri.password else ''
    db_name = puri.path.split('/')[1]
    conn_pool = redis.ConnectionPool(host=host, port=port, password=password, db=db_name)
    return redis.Redis(connection_pool=conn_pool)



class Cache(object):
    """
    redis缓存
    """
    def __init__(self, uri=None):
        self.uri = uri if uri else REDIS_CACHE_URL
        self.connection = connect_redis(self.uri)

    def check_connect(self):
        try:
            return self.connection.ping()
        except Exception as e:
            return False

    def get_pipe(self):
        return self.connection.pipeline()

    def get_keys(self):
        return self.connection.keys()

    def delete_key(self, key):
        self.connection.delete(key)

    def set_push(self, key, value):
        self.connection.sadd(key, value)

    def exist_in_set(self, key, value):
        return self.connection.sismember(key, value)

    def set_pop(self, key):
        value = self.connection.spop(key)
        if value:
            return value
        else:
            return None

    def get_set_num(self, key):
        return self.connection.scard(key)

    def list_push(self, key, *values):
        pipe = self.get_pipe()
        for value in values:
            pipe.rpush(key, value)
        return pipe.execute()

    def list_push_by_one(self, key, value):
        self.connection.rpush(key, value)

    def list_lpop(self, key):
        value = self.connection.blpop(key, timeout=3)
        if value:
            return value[1]
        else:
            return None

    def get_list_num(self, key):
        return self.connection.llen(key)


if __name__ == '__main__':

    test_proxy('45.79.0.108', '1080')