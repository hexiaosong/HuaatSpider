# coding: utf-8
"""
Create on 2017/10/2

@author:hexiaosong
"""

import time
import re
import requests
from bson import json_util


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


if __name__ == '__main__':

    test_proxy('45.79.0.108', '1080')