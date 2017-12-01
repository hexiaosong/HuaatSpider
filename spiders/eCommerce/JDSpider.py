# coding: utf-8
"""
Create on 2017/11/23

@author:hexiaosong
"""

from __future__ import unicode_literals

import os
import re
import time
import random
import socket
import urllib2
from spiders import logging as logger
from utils.common import jprint
from splinter import Browser
from lxml import etree
from JD_app import app
from db.mongodb.models import (JDvisitedUrl, JDeCommerceSpider)

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 BIDUBrowser/6.x Safari/537.31',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.44 Safari/537.36 OPR/24.0.1558.25 (Edition Next)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36 OPR/23.0.1522.60 (Edition Campaign 54)',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
]


class JDSpiderAnother():

    name = 'JD_spider_another'

    ele_xpath_dict = {
        'prd_name': '//div[contains(@class,"p-name")]/a/em/text()',
        'prd_id': '//a[@class="J_focus"]/@data-sku',
        'price': '//div[@class="p-price"]/strong/i/text()',
        'prd_href': '//div[contains(@class,"p-name")]/a/@href',
    }

    def __init__(self,
                 cate_page_url=None,
                 cates=None,
                 version='201711',
                 browser=None,
                 **kwargs):
        self.url = cate_page_url
        self.cates = cates
        self.version = version
        self.browser = browser

    @staticmethod
    def find_by_xpath(etree, ele_xpath):
        result = etree.xpath(ele_xpath)
        if result:
            tmp = [item for item in result if item.strip()]
            return tmp[0].strip()
        else:
            return ''

    @staticmethod
    def openurl(url):
        user_agent = random.choice(user_agents)
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Connection': 'keep-alive',
                   'User-Agent': user_agent,
                   }
        match = re.search(r'^http[s]{0,}://.*', url)
        if match:
            url_tmp = url
        else:
            url_tmp = "http:" + url
        req = urllib2.Request(url_tmp, headers=headers)

        response = urllib2.urlopen(req)
        html = response.read()
        response.close()

        return html

    def get_url_list(self, page_num):
        """
        组合页面url
        :param page_num:
        :return:
        """
        base_url = self.url.split('&sort=')[0]
        suffix = '&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main'
        page_url_list = ['{}&page={}{}'.format(base_url, index + 1, suffix) for index in range(int(page_num))]

        return page_url_list

    def get_branch_info(self, prd_href):

        branch = {"branch_name":'', "branch_id":''}
        inner_html = self.openurl(prd_href)
        inner_html = inner_html.decode('gb18030')

        base_xpath = '//div[@class="crumb fl clearfix"]//a[contains(@href,"ev=exbrand")]/'
        detail_page_tree = etree.HTML(inner_html)
        branch["branch_name"] = self.find_by_xpath(detail_page_tree, base_xpath+ 'text()')
        branch_id_tmp = self.find_by_xpath(detail_page_tree, base_xpath+ '@href')
        if branch_id_tmp:
            branch["branch_id"] = re.search('ev=exbrand_(\d+)', branch_id_tmp).group(1)

        return branch

    def parseEngine(self):

        good_xpath = '//*[@id="plist"]/ul/li'

        if not JDvisitedUrl.objects.filter(url=self.url, version=self.version):
            self.browser.visit(self.url, 90)
        else:
            logger.info('此url:{}已经访问过了！'.format(self.url))
            return

        if '抱歉，没有找到相关的商品' in self.browser.html:
            logger.info('此类别没有找到相关的商品！'.format(self.cate_page_url))
            return

        try:
            page_num = self.browser.find_by_xpath('//div[@id="J_bottomPage"]/span/em/b').value
        except AttributeError:
            page_num = 1

        page_url_list = self.get_url_list(page_num)

        for page, url in enumerate(page_url_list):

            logger.info('当前类别 ==> {}'.format(self.cates))
            logger.info('共{}页, 正在爬取第{}页...'.format(len(page_url_list),page + 1))

            if not JDvisitedUrl.objects.filter(url=url, version=self.version):
                if self.browser.is_element_present_by_css('.pn-next') and page > 0:
                    self.browser.find_by_xpath('//*[@id="page_jump_num"]').fill(page + 1)
                    time.sleep(1)
                    if len(self.browser.windows)==2:
                        self.browser.windows[1].close()
                    time.sleep(1)
                    self.browser.find_by_css('.pn-next').click()
                    time.sleep(1)
                    if len(self.browser.windows)==2:
                        self.browser.windows[1].close()
                    COUNT = 0
                    while not self.browser.is_element_present_by_id('page_jump_num') and COUNT<3:
                        time.sleep(2)
                        COUNT += 1

                prd_list = self.browser.find_by_xpath(good_xpath)
                if prd_list:
                    for index, prd in enumerate(prd_list):
                        d = {}
                        ele_tree = etree.HTML(prd.html)
                        for k, v in self.ele_xpath_dict.items():
                            d[k] = self.find_by_xpath(ele_tree, v)
                        logger.info(jprint(d))

                        prd_href = d.get('prd_href','')
                        branch = {"branch_name": '', "branch_id": ''}
                        if prd_href:
                            branch = self.get_branch_info(prd_href)

                        hive_str = "1\t{cates}\t{branch_id}\t{branch_name}\t{prd_id}\t{prd_name}\t{price}".format(
                            cates=self.cates,
                            branch_id=branch.get('branch_id', ''),
                            branch_name=branch.get('branch_name', ''),
                            prd_id=d.get('prd_id', ''),
                            prd_name=d.get('prd_name', ''),
                            price=d.get('price', '')
                        )
                        db_item = JDeCommerceSpider(platform=self.name, url=url,
                                                  version=self.version, hive_str=hive_str)
                        if not JDeCommerceSpider.objects.filter(platform=self.name, url=url,
                                                              version=self.version, hive_str=hive_str):
                            db_item.save()
                if not JDvisitedUrl.objects.filter(url=url, version=self.version):
                    JDvisitedUrl(url=url, version=self.version).save()
            else:
                logger.info('网页链接已经访问!%s' % url)

        JDvisitedUrl(url=self.url, version=self.version).save()



@app.task(name='jd_spider', queue='jd_spider')
def jd_spider(data):
    logger.info("func get args: %s" % data)
    b = Browser('chrome')
    try:
        spider = JDSpiderAnother(cate_page_url=data.get('cate_page_url'),
                                cates=data.get('cates'),
                                browser=b,
                                )
        spider.parseEngine()
    except Exception,e:
        logger.error(str(e))
    spider.browser.quit()

