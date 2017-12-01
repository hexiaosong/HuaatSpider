# coding: utf-8
"""
Create on 2017/11/15

@author:hexiaosong
"""
from __future__ import unicode_literals

import re
from fabric.api import *
from fabric.colors import *
from spiders import PROJECT_ROOT
from utils.common import yesterday_date


WINXIN_DATA_DIR = '{}/data/articles'.format(PROJECT_ROOT)
env.hosts = ['106.75.85.39',]
env.user = ''
env.password = ''
env.port=5123
env.winxin_data_dir='/data/hive_home/winxin_data'


def test():
    """测试"""
    print green("Hello World !")


def query_hive(date_str):
    """
    hive数据查询
    :param date_str:
    :return:
    """
    query_hql = """hive -e 'use dmp; select * from dmp.gzh where `date`={date_str} limit 10;'""".format(
        date_str=date_str)
    print green(query_hql)
    run(query_hql)


def _hive_operate(date, date_simple):
    load_hql = """hive -e 'use dmp; load data local inpath "/data/hive_home/winxin_data/data_{date}.txt" overwrite into table dmp.wxb;'""".format(
        date=date)
    insert_hql = """hive -e 'use dmp; INSERT INTO TABLE dmp.gzh PARTITION (`date`={date_simple}) select * from wxb;'""".format(
        date_simple=date_simple)
    query_hql = """hive -e 'use dmp; select * from dmp.gzh where `date`={date_simple} limit 10;'""".format(
        date_simple=date_simple)

    print green(load_hql)
    print green(insert_hql)
    print green(query_hql)

    run(load_hql)
    print green('数据成功加载至临时表dmp.wxb中...')
    run(insert_hql)
    print green('将临时表数据已经插入表dmp.gzh中...')
    run(query_hql)


def winxin2hive(date=None):
    """
    上传微信公众号爬虫数据至hive
    :return:
    """
    if not date:
        date = yesterday_date()
    date_simple = re.sub('_','',date)
    data_dir = '{}/{}'.format(WINXIN_DATA_DIR, date)
    data_file = '{}/data_{}.txt'.format(data_dir, date)

    if os.path.exists(data_dir) and os.path.getsize(data_file)>0:
        # data_file = '{}/data_{}.txt'.format(data_dir, date)
        run('pwd')
        upload_file_path = env.winxin_data_dir + '/data_{}.txt'.format(date)
        if int(run(" [ -e '{}' ] && echo 1 || echo 0".format(upload_file_path))) == 0:
            result = put(data_file, env.winxin_data_dir)
            if not result.failed:
                print green('文件上传成功！')
                _hive_operate(date, date_simple)
            else:
                print red('数据文件{}未传至服务器.')
        else:
            print red('文件在服务器已经存在！')
    else:
        print red('日期{}的公众号爬虫数据不存在或文件为空！'.format(date))