# coding: utf-8
"""
Create on 2017/10/5

@author:hexiaosong
"""
import datetime
from mongoengine import *

class WinxinData(Document):
    """
    @summary: 微信公众号爬虫数据
    """
    host = StringField(required=False, verbose_name='爬虫主机名')
    source = StringField(default='', verbose_name='平台来源')
    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='爬取时间',
    )
    category = StringField(default='', verbose_name='行业类别')
    public_id = StringField(default='', verbose_name='公众号id')
    article_title = StringField(default='', verbose_name='文章标题')
    public_name = StringField(default='', verbose_name='公众号')
    spread_index = FloatField(default=0.0, verbose_name='传播指数')
    reading_quantity = StringField(default='', verbose_name='阅读量')
    point_number = IntField(required=False, default=0, verbose_name='点赞数')

