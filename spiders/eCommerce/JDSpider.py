# coding: utf-8
"""
Create on 2017/11/23

@author:hexiaosong
"""

from __future__ import unicode_literals

import re
import time
import random
import urllib2
from spiders import logging as logger
from utils.common import jprint
from splinter import Browser
from lxml import etree
from selenium.webdriver.chrome.options import Options
from app import app
from db.mongodb.models import (JDvisitedUrl, JDeCommerceSpider)
from data.agents import user_agents


class JDSpiderAnother():

    name = 'JD_spider_another'

    ele_xpath_dict = {
        'prd_name': '//div[contains(@class,"p-name")]/a/em/text()',
        'prd_id': '//a[contains(@class,"J_focus")]/@data-sku',
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
        response = urllib2.urlopen(req, timeout=60)
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
        count = 0
        while not inner_html and count<3:
            time.sleep(2)
        try:
            inner_html = inner_html.decode('gb18030', 'ignore')
        except Exception as e:
                pass

        base_xpath = '//div[@class="crumb fl clearfix"]//a[contains(@href,"ev=exbrand")]/'
        detail_page_tree = etree.HTML(inner_html)
        branch["branch_name"] = self.find_by_xpath(detail_page_tree, base_xpath+ 'text()')
        branch_id_tmp = self.find_by_xpath(detail_page_tree, base_xpath+ '@href')
        if branch_id_tmp:
            id_tmp = re.search('ev=exbrand_(\d+)', branch_id_tmp)
            if id_tmp:
                branch["branch_id"] = id_tmp.group(1)

        if not branch["branch_id"]:
            tmp = re.search('ecomm_pbrand:(\d+)', inner_html)
            if tmp:
                branch["branch_id"] = tmp.group(1)

        if not branch["branch_name"]:
            branch["branch_name"] = self.find_by_xpath(detail_page_tree, '//div[contains(@class,"ellipsis")]/text()')
            if branch["branch_name"]:
                tmp = re.search('product|mbNav-4">\s*(\S+)\s*</a>', inner_html)

        return branch

    def parseEngine(self):

        good_xpath = '//*[@id="plist"]/ul/li'

        if not JDvisitedUrl.objects.filter(url=self.url, version=self.version):
            self.browser.visit(self.url, 90)
            if '加油！您和宝贝只有一个验证码的距离啦！' in self.browser.html:
                self.browser.find_by_xpath('//a[@class="ui-dialog-close"]').click()
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
                        try:
                            d = {}
                            ele_tree = etree.HTML(prd.html)
                            for k, v in self.ele_xpath_dict.items():
                                d[k] = self.find_by_xpath(ele_tree, v)
                            logger.info(jprint(d))

                            prd_href = d.get('prd_href','')
                            branch = {"branch_name": '', "branch_id": ''}
                            if prd_href:
                                branch = self.get_branch_info(prd_href)
                                if not branch['branch_name'] and not branch['branch_id']:
                                    branch = self.get_branch_info(prd_href)
                                logger.info(jprint(branch))

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
                            #if not JDeCommerceSpider.objects.filter(platform=self.name, url=url,
                            #                                      version=self.version, hive_str=hive_str):
                            db_item.save()
                        except Exception,e:
                            logger.error(str(e))
                if not JDvisitedUrl.objects.filter(url=url, version=self.version):
                    JDvisitedUrl(url=url, version=self.version).save()
            else:
                logger.info('网页链接已经访问!%s' % url)

        JDvisitedUrl(url=self.url, version=self.version).save()



@app.task(name='jd_spider', queue='jd_spider')
def jd_spider(data, is_headless=False):
    logger.info("func get args: %s" % data)
    if is_headless:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        b = Browser('chrome',options = chrome_options)
    else:
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

