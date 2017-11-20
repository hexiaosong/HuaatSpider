# coding: utf-8
"""
Create on 2017/10/2

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
    spread_index = StringField(default='--', verbose_name='传播指数')
    reading_quantity = StringField(default='', verbose_name='阅读量')
    point_number = IntField(required=False, default=0, verbose_name='点赞数')

    meta = {
        'db_alias': "HuaatSpiders",
        'strict': False,
        'index_background': True,
        "collection": "winxin_data",
        "indexes": [
            "-add_time",
            "source",
            "article_title",
            'public_name',
            "spread_index",
            "reading_quantity",
            "point_number",
            # {
            #     "fields": ("article_title", "public_name"),
            #     "unique": True,
            # },
        ]
    }

    def __unicode__(self):

        return '%s %s %s %s %s %s' % \
               (self.add_time,
                self.article_title,
                self.public_name,
                self.spread_index,
                self.reading_quantity,
                self.point_number,
                )


class SouguoArticle(Document):

    host = StringField(required=False, verbose_name='爬虫主机名')
    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='爬取时间',
    )
    expand_word = StringField(required=False, verbose_name='扩展搜索词')
    url = StringField(required=False, verbose_name='爬取网页url')
    html = StringField(required=False, verbose_name='原始网页')
    article_title = StringField(required=False, verbose_name='文章标题')
    weixin_name = StringField(required=False, verbose_name='微信号')
    content = StringField(required=False, verbose_name='网页文本')

    meta = {
        'db_alias': "HuaatSpiders",
        "collection": "SouguoArticles",
        'strict': False,
        'index_background': True,
        "indexes": [
            "-add_time",
            "url",
            "html",
            "content",
        ]
    }

    def __unicode__(self):
        return u'<SouguoArticle {} {} {}>'.format(self.id, self.add_time, self.url)

    def exist_url(self):
        urls = self.objects(url=self.url).order_by('-add_time')
        if urls:
            return True
        else:
            return False



class SouguoArticleUrl(Document):

    STATUS_CHOICES = [
        (0, '未爬取'),
        (1, '已爬取'),
        (2, '链接失效')
    ]

    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='爬取时间',
    )
    expand_word = StringField(required=False, verbose_name='扩展词')
    title = StringField(required=False, verbose_name='文章标题')
    winxin_ch_name = StringField(required=False, verbose_name='微信中文名')
    publish_date = StringField(required=False, verbose_name='文章发表日期')
    url = StringField(required=False, verbose_name='文章链接')
    status = IntField(default=0, choices=STATUS_CHOICES, verbose_name='爬取状态')
    meta = {
        'db_alias': "HuaatSpiders",
        "collection": "SouguoArticleUrl",
        'strict': False,
        'index_background': True,
        "indexes": [
            "-add_time",
            "url",
            "winxin_ch_name",
            "status",
        ]
    }
    def __unicode__(self):
        return u'<SouguoArticleUrl {} {} {} {}>'.format(self.id, self.title, self.winxin_ch_name, self.publish_date)

