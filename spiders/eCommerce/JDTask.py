# coding: utf-8
"""
Create on 2017/12/1

@author:hexiaosong
"""

import re
from app import app
from spiders import PROJECT_ROOT


def readDictfile(filename):
    import codecs
    file = codecs.open(filename, "r", encoding='gb2312')
    dict_t={}
    for i in file:
        m = re.split(r':', i , 1)
        dict_t[m[0]] = m[1].strip('\n')
    file.close()
    return dict_t

if __name__ == '__main__':
    file_path = '%s/data/eCommerce/JD/JD_category.txt' % PROJECT_ROOT
    all_url_data = readDictfile(file_path)
    for k,v in all_url_data.items():
        send_data = {
            "cate_page_url": 'http://%s' % k,
            "cates": v,
        }
        app.send_task('jd_spider', args=(send_data,))