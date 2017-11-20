# coding: utf-8
"""
Create on 2017/11/20

@author:hexiaosong
"""

from __future__ import  unicode_literals

from subprocess import Popen
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.common import yesterday_date


sched = BlockingScheduler()


# @sched.scheduled_job('cron', day_of_week='1-7', hour=13, minute=10, second=0)
@sched.scheduled_job('interval', hours=6)
def cron_upload_wx_spider():
    date = yesterday_date()
    shell_cmd = 'fab winxin2hive:{}'.format(date)
    Popen(shell_cmd, shell=True)
    # Popen.wait()

if __name__ == '__main__':
    print 'starting upload winxin_data to hive...'
    sched.start()
