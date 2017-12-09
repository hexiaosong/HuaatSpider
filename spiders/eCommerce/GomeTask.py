# coding: utf-8
"""
Create on 2017/12/3

@author:hexiaosong
"""

import re
from spiders.eCommerce.app import app
from spiders import PROJECT_ROOT


def readDictfile(filename):
    import codecs
    file = codecs.open(filename, "r", encoding='utf-8')
    dict_t={}
    for i in file:
        m = re.split(r':', i , 1)
        dict_t[m[0]] = m[1].strip('\n')
    file.close()
    return dict_t

if __name__ == '__main__':
    file_path = '%s/data/eCommerce/gome/gome_category.txt' % PROJECT_ROOT
    all_url_data = readDictfile(file_path)
    for k,v in all_url_data.items():
        core_str = re.search('(cat\d+).html', k).group(1)
        k = 'http://list.gome.com.cn/{}.html?intcmp=list-'.format(core_str)
        send_data = {
            "cate_page_url": k,
            "cates": v,
        }
        app.send_task('gome_spider', args=(send_data,))