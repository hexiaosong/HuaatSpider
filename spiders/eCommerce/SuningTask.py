# coding: utf-8
"""
Create on 2017/12/3

@author:hexiaosong
"""

import re
from spiders.eCommerce.app import app
import codecs
import random
from spiders import PROJECT_ROOT


def readDictfile(filename):

    file = codecs.open(filename, "r", encoding='utf-8').readlines()
    random.shuffle(file)
    dict_t={}
    for i in file:
        m = re.split(r':', i , 1)
        if 'list' in m[0]:
            dict_t[m[0]] = m[1].strip('\n')

    return dict_t

if __name__ == '__main__':
    file_path = '%s/data/eCommerce/suning/suning_category.txt' % PROJECT_ROOT
    all_url_data = readDictfile(file_path)
    for k,v in all_url_data.items():
        if 'http' not in k:
            k = 'http://' + k
        send_data = {
            "cate_page_url": k,
            "cates": v,
        }
        app.send_task('suning_spider', args=(send_data,))