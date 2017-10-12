# coding: utf-8
"""
Create on 2017/10/12

@author:hexiaosong
"""
from __future__ import unicode_literals

import re
import time
import random
from collections import OrderedDict
from bs4 import BeautifulSoup
from splinter import Browser
from spiders import logging
from utils.common import jprint
from settings.settings_local import HOSTNAME
from preprocess import extract_html
from db.mongodb.models import SouguoArticle
from data.WeixinData.ExpandWords import EXPAND_WORDS_LIST



class SougouArticleSpider(object):

    spider_name = 'SougouArticleSpider'
    search_url = 'http://weixin.sogou.com/'

    def __init__(self, expand_words=None, browser_type='chrome', logging=logging):
        self.expand_words = expand_words
        self.driver_kwargs = {}
        self.logger = logging
        self.browser = Browser(browser_type)

    def create_browser(self, browser_type):
        try:
            self.driver_kwargs.update({'driver_name': browser_type, })
            b = Browser(browser_type)
            self.logger.debug('creating browser {}'.format(self.driver_kwargs))
        except Exception,e:
            self.logger.info('退出异常的%s浏览器' % self.spider_name)
            self.browser.quit()
            del self.browser


    def get_search_url(self):
        """
        获取所有扩展关键词的文章url
        :return:
        """
        expand_word_urls = OrderedDict()

        for word in self.expand_words:
            complete_url = '{}/weixin?type=2&s_from=input&query={}&ie=utf8&_sug_=n&_sug_type_='.format(self.search_url, word)
            expand_word_urls[word] = complete_url
            # jprint(expand_word_urls)
        return expand_word_urls


    def crawl_articles(self, expand_word_url=None, is_login=True, wait_time=5, index_page=True):
        """
        爬取单个搜索扩展关键词文章
        :param expand_word_url:
        :return:
        """
        article_urls = []

        if index_page:
            self.browser.visit(expand_word_url, timeout=10)

            if is_login:
                self.browser.visit(self.search_url)
                time.sleep(random.randint(2,4))
                try:
                    self.browser.find_by_xpath('//a[@id="loginBtn"]').click()
                    self.logger.info("使用手机微信扫描登录...")
                    time.sleep(wait_time)
                except Exception,e:
                    pass

                self.browser.visit(expand_word_url, timeout=10)

        html = self.browser.html
        soup = BeautifulSoup(html)

        container = soup.findAll("ul",{"class":"news-list"})
        if container:
            article_element = container[0].findAll("li")
            for node in article_element:
                try:
                    href = node.div.a.attrs['href']
                    title_text = node.find("div",{"class":"txt-box"}).h3.a.get_text()
                    title = re.sub('[ \n\r(red_beg)(red_end)]','', title_text)
                    if not SouguoArticle.objects.filter(article_title__contains=title):
                        article_urls.append(href)
                except KeyError,e:
                    self.logger.error('节点无href属性.{}'.format(node.prettify()))
                except Exception,e:
                    self.logger.error('Error: {} \n {}'.format(node.prettify(), unicode(e)))

        return article_urls


    def get_next_page(self):

        current_url = self.browser.url
        if 'page' not in current_url:
            current_url = '%s&page=1' % current_url
        reg_match = re.search('&page=(\d+)', current_url)
        if reg_match:
            cur_page_num = int(reg_match.group(1))
            next_page_num = cur_page_num +1
            next_page_url = re.sub('&page=(\d+)', '&page=%s' % next_page_num, current_url)
        if self.browser.is_element_present_by_id('sogou_next'):
            self.browser.visit(next_page_url, timeout=10)
            time.sleep(random.randint(5,10))
            return True
        else:
            self.logger.info('当前页面%s为最后一页' % current_url)
            return False


    def extract_detail_page(self, detail_page_url, rand_waiting=(2,5), expand_word='', ):
        """
        爬取详情页
        :param detail_page_url:
        :param waiting:
        :param expand_word:
        :return:
        """
        self.browser.visit(detail_page_url, timeout=10)
        html = self.browser.html
        url = self.browser.url

        result = extract_html(html)
        tail_str = u'赞赏长按二维码向我转账受苹果公司新规定影响，微信iOS版的赞赏功能被关闭，可通过二维码转账支持公众号。'
        content = result.get("clean_content").replace(tail_str, '')

        time.sleep(random.randint(rand_waiting[0], rand_waiting[1]))

        kwargs = {
            'host':HOSTNAME,
            'expand_word':expand_word,
            'url':url,
            'html':html,
            'weixin_name':result.get("name"),
            'article_title':result.get("article_title"),
            'content':content
        }
        jprint(kwargs)
        try:
            arcticle = SouguoArticle(**kwargs)
            if not SouguoArticle.objects.filter(article_title=result.get("article_title")):
                arcticle.save()
            self.logger.info(arcticle)
        except Exception,e:
            self.logger.error('Save arcticle error: %s' % unicode(e))



def main(page_num=50):

    spider = SougouArticleSpider(expand_words=EXPAND_WORDS_LIST)
    search_urls = spider.get_search_url()
    for expand_word, search_url in search_urls.items():
        article_page_urls = []
        article_page_urls.extend(spider.crawl_articles(expand_word_url = search_url))
        count = 1
        while spider.get_next_page() and count<=page_num:
            article_page_urls.extend(spider.crawl_articles(index_page=False))
            count += 1

        for detail_url in article_page_urls:
            try:
                spider.extract_detail_page(detail_page_url=detail_url, expand_word=expand_word)
            except Exception,e:
                spider.logger.error('Error: %s' % unicode(e))
                continue




if __name__ == '__main__':

    main()