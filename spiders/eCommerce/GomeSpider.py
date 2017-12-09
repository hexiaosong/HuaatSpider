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
from selenium.webdriver.chrome.options import Options
from splinter import Browser

from db.mongodb.models import (GomevisitedUrl, GomeCommerceSpider)
from spiders import logging as logger
from spiders.eCommerce.app import app
from utils.common import jprint
from data.agents import user_agents

class GomeSpider():

    name = 'gome_spider'

    ele_xpath_dict = {
        'prd_name': '//p[contains(@class,"item-name")]/a/text()',
        'prd_id': '//input[contains(@class,"productInfo")]/@skuid',
        'price': '//p[@class="item-price"]/span/text()',
        'prd_href': '//p[contains(@class,"item-pic")]/a/@href',
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
        response = urllib2.urlopen(req, timeout=10)
        html = response.read()
        response.close()

        return html

    def get_branch_info(self, prd_href):

        branch = {"brand_name":'', "brand_id":''}
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

    def scroll_down(self):
        for _ in range(1, 9):
            self.browser.execute_script('window.scrollBy(0,%s)' % 700)
            time.sleep(1.5)


    def parseEngine(self):

        good_xpath = '//div[@class="product-box"]/ul/li'

        cate_str_split = self.cates.split('\t')
        level1 = cate_str_split[0]
        level2 = cate_str_split[1]
        level3 = cate_str_split[2]
        level3_id = cate_str_split[3]

        if not GomevisitedUrl.objects.filter(url=self.url, flag_cate=1, version=self.version):
            self.browser.visit(self.url, 90)
        else:
            logger.info('此url:{}已经访问过了！'.format(self.url))
            return

        if '抱歉，没有找到相关的商品' in self.browser.html:
            logger.info('此类别没有找到相关的商品！'.format(self.cate_page_url))
            return

        self.scroll_down()
        try:
            cate_tree = etree.HTML(self.browser.html)
            page_tmp = self.find_by_xpath(cate_tree, '//div[@class="pager"]/a[last()-2]/text()')
            page_num = page_tmp if page_tmp else 1
        except AttributeError:
            page_num = 1

        for page in range(int(page_num)):

            logger.info('当前类别 ==> {}'.format(self.cates))
            logger.info('共{}页, 正在爬取第{}页...'.format(page_num, page + 1))

            if not GomevisitedUrl.objects.filter(url=self.url, page=(page+1), version=self.version):
                if self.browser.is_element_present_by_xpath('//div[@class="pager"]/a[@class="next"]') and page > 0:
                    self.browser.find_by_xpath('//input[@id="pNum"]').fill(page + 1)
                    time.sleep(1)
                    if len(self.browser.windows)==2:
                        self.browser.windows[1].close()
                    time.sleep(1)
                    try:
                        self.browser.find_by_xpath('//div[@class="pager"]/a[@class="next"]').click()
                    except Exception,e:
                        self.browser.find_by_xpath('//div[@class="pager"]/a[@class="btn"]').click()
                    time.sleep(1)
                    if len(self.browser.windows)==2:
                        self.browser.windows[1].close()
                    self.scroll_down()

                prd_list = self.browser.find_by_xpath(good_xpath)
                if prd_list:
                    for index, prd in enumerate(prd_list):
                        d = {}
                        ele_tree = etree.HTML(prd.html)
                        for k, v in self.ele_xpath_dict.items():
                            d[k] = self.find_by_xpath(ele_tree, v)
                        d["price"] = d["price"].replace("¥", "") if d["price"] else ''
                        logger.info(jprint(d))

                        prd_href = d.get('prd_href','')
                        brand = {"brand_name": '', "brand_id": ''}
                        # if prd_href:
                        #     branch = self.get_branch_info(prd_href)
                        #     if not branch['branch_name'] and not branch['branch_id']:
                        #         branch = self.get_branch_info(prd_href)
                        #     logger.info(jprint(branch))

                        hive_str = "4" +'\t'+ "" +'\t'+ level1 +'\t'+ "" +'\t'+ level2 +'\t'+ level3_id +'\t'+ level3 \
                                   +'\t'+ brand.get("brand_id") + '\t' + brand.get("brand_name") + '\t' + \
                                   d.get("prd_id","") + '\t' + d.get("prd_name","") + '\t' + d.get("price")
                        logger.info(hive_str)
                        db_item = GomeCommerceSpider(platform=self.name,version=self.version, hive_str=hive_str)
                        if not GomeCommerceSpider.objects.filter(platform=self.name, version=self.version, hive_str=hive_str):
                            db_item.save()
                if not GomevisitedUrl.objects.filter(url=self.url, page=(page+1), version=self.version):
                    GomevisitedUrl(url=self.url, page=(page+1), version=self.version).save()
            else:
                logger.info('网页链接已经访问!%s' % self.url)

        GomevisitedUrl(url=self.url, flag_cate=1, version=self.version).save()

@app.task(name='gome_spider', queue='gome_spider')
def gome_spider(data, is_headless=False):
    logger.info("func get args: %s" % data)
    if is_headless:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        b = Browser('chrome', options=chrome_options)
    else:
        b = Browser('chrome')
    b.driver.set_window_size(1250, 1000)
    try:
        spider = GomeSpider(cate_page_url=data.get('cate_page_url'),
                                cates=data.get('cates'),
                                browser=b,
                                )
        spider.parseEngine()
    except Exception,e:
        logger.error(str(e))
    spider.browser.quit()


if __name__ == '__main__':
    from spiders.eCommerce.GomeTask import readDictfile
    from spiders import PROJECT_ROOT
    file_path = '%s/data/eCommerce/gome/gome_category.txt' % PROJECT_ROOT
    all_url_data = readDictfile(file_path)
    for k, v in all_url_data.items():
        core_str = re.search('(cat\d+).html', k).group(1)
        k = 'http://list.gome.com.cn/{}.html?intcmp=list-'.format(core_str)
        d = {
            "cate_page_url": k,
            "cates": v,
        }
        gome_spider(d)