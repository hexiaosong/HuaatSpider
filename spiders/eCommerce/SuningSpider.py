# coding: utf-8
"""
Create on 2017/12/3

@author:hexiaosong
"""
from __future__ import unicode_literals

import random
import time
import urllib2

import re
from lxml import etree
from splinter import Browser

from db.mongodb.models import (SuningvisitedUrl, SuningeCommerceSpider)
from spiders import logging as logger
from spiders.eCommerce.app import app
from utils.common import jprint
from data.agents import user_agents

class SuningSpider():

    name = 'suning_spider'

    ele_xpath_dict = {
        'prd_name': '//div[@class="res-info"]/p/a[@class="sellPoint"]/text()',
        'prd_id': '//input[contains(@class,"productInfo")]/@skuid',
        'prd_href': '//p[contains(@class,"sell-point")]/a/@href',
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
        html = ''
        try:
            response = urllib2.urlopen(req, timeout=10)
            html = response.read()
            response.close()
        except Exception,e:
            pass

        return html

    def get_brand_info(self, prd_href):

        brand = {"brand_name":'', "brand_id":''}
        inner_html = self.openurl(prd_href)
        count = 0
        while not inner_html and count<3:
            time.sleep(2)

        try:
            inner_html = inner_html.decode('utf-8', 'ignore')
        except Exception as e:
                pass

        id_tmp = re.search('"brandCode":"([0-9A-Z]+)",', inner_html)
        if id_tmp:
            brand["brand_id"] = id_tmp.group(1)

        name_tmp = re.search('"brandName":"(\S+)"', inner_html)
        if name_tmp:
            brand["brand_name"] = name_tmp.group(1)

        return brand

    def parseEngine(self):

        good_xpath = '//div[@id="filter-results"]/ul/li'

        cate_str_split = self.cates.split('\t')
        level1_name=cate_str_split[0]
        level2_code = cate_str_split[1]
        level2_name = cate_str_split[2]
        level3_code = cate_str_split[3]
        level3_name = cate_str_split[4]

        if not SuningvisitedUrl.objects.filter(url=self.url, flag_cate=1, version=self.version):
            self.browser.visit(self.url, 90)
        else:
            logger.info('此url:{}已经访问过了！'.format(self.url))
            return

        if '非常抱歉！没有找到符合条件的商品' in self.browser.html:
            logger.info('此类别没有找到相关的商品！'.format(self.cate_page_url))
            return

        try:
            cate_tree = etree.HTML(self.browser.html)
            page_tmp = self.find_by_xpath(cate_tree, '//div[@id="bottom_pager"]/a[last()-2]/text()')
            page_num = page_tmp if page_tmp else 1
        except AttributeError:
            page_num = 1

        for page in range(int(page_num)):

            logger.info('当前类别 ==> {}'.format(self.cates))
            logger.info('共{}页, 正在爬取第{}页...'.format(page_num, page + 1))

            if not SuningvisitedUrl.objects.filter(url=self.url, page=(page+1), version=self.version):
                if self.browser.is_element_present_by_xpath('//div[@id="bottom_pager"]/a[@id="nextPage"]') and page > 0:
                    self.browser.find_by_xpath('//input[@id="pNum"]').fill(page + 1)
                    time.sleep(1)
                    if len(self.browser.windows)==2:
                        self.browser.windows[1].close()
                    time.sleep(1)
                    self.browser.find_by_xpath('//a[contains(@class,"page-more")]').click()
                    time.sleep(1)
                    if len(self.browser.windows)==2:
                        self.browser.windows[1].close()

                prd_list = self.browser.find_by_xpath(good_xpath)
                if prd_list:
                    for index, prd in enumerate(prd_list):
                        d = {"price":""}
                        ele_tree = etree.HTML(prd.html)
                        for k, v in self.ele_xpath_dict.items():
                            d[k] = self.find_by_xpath(ele_tree, v)
                        d['price'] = self.browser.find_by_xpath('//p[@class="prive-tag"]/em').value
                        d["price"] = d["price"].replace("¥", "").strip('\n') if d["price"] else ''

                        prd_href = d.get('prd_href','')
                        brand = {"brand_name": '', "brand_id": ''}
                        if prd_href:
                            d['prd_id'] = re.search('(\d+).html', prd_href).group(1)
                            logger.info(jprint(d))
                            brand = self.get_brand_info(prd_href)
                            if not brand['brand_name'] and not brand['brand_id']:
                                brand = self.get_brand_info(prd_href)
                            logger.info(jprint(brand))

                        hive_str = "3" +'\t'+ "" +'\t'+ level1_name +'\t'+ level2_code +'\t'+ level2_name +'\t'+ level3_code +'\t'+ level3_name \
                                   +'\t'+ brand.get("brand_id") + '\t' + brand.get("brand_name") + '\t' + \
                                   d.get("prd_id","") + '\t' + d.get("prd_name","") + '\t' + d.get("price")
                        logger.info(hive_str)
                        db_item = SuningeCommerceSpider(platform=self.name,version=self.version, hive_str=hive_str)
                        if not SuningeCommerceSpider.objects.filter(platform=self.name, version=self.version, hive_str=hive_str):
                            db_item.save()
                if not SuningvisitedUrl.objects.filter(url=self.url, page=(page+1), version=self.version):
                    SuningvisitedUrl(url=self.url, page=(page+1), version=self.version).save()
            else:
                logger.info('网页链接已经访问!%s' % self.url)

        SuningvisitedUrl(url=self.url, flag_cate=1, version=self.version).save()

@app.task(name='suning_spider', queue='suning_spider')
def suning_spider(data):
    logger.info("func get args: %s" % data)
    b = Browser('chrome')
    try:
        spider = SuningSpider(cate_page_url=data.get('cate_page_url'),
                                cates=data.get('cates'),
                                browser=b,
                                )
        spider.parseEngine()
    except Exception,e:
        logger.error(str(e))
    spider.browser.quit()


if __name__ == '__main__':
    from spiders.eCommerce.SuningTask import readDictfile
    from spiders import PROJECT_ROOT
    file_path = '%s/data/eCommerce/suning/suning_category.txt' % PROJECT_ROOT
    all_url_data = readDictfile(file_path)
    for k, v in all_url_data.items():
        d = {
            "cate_page_url": 'http://' + k,
            "cates": v,
        }
        suning_spider(d)