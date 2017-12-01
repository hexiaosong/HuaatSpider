# coding: utf-8
"""
Create on 2017/11/20

@author:hexiaosong
"""

from __future__ import  unicode_literals

from subprocess import Popen
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.common import yesterday_date
from spiders import PROJECT_ROOT


sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=6)
def cron_upload_wx_spider():
    date = yesterday_date()
    print 'yesterday is %s' % date
    file_handle = open("{}/log/upload_wx_hive.log".format(PROJECT_ROOT), 'w+')
    shell_cmd = 'fab winxin2hive:{}'.format(date)
    Popen(shell_cmd, shell=True, stdout=file_handle)

if __name__ == '__main__':
    print 'starting upload winxin_data to hive...'
    sched.start()
