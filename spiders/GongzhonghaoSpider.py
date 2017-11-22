# coding: utf-8
"""
Create on 2017-09-27 

@author:hexiaosong
"""

from __future__ import  unicode_literals

import codecs
import random
from collections import OrderedDict
from splinter import Browser
from apscheduler.schedulers.blocking import BlockingScheduler
from spiders import *
from utils.common import *
from settings.settings_local import HOSTNAME
from data.WeixinData.gongzhonghao import *
from db.mongodb.models import WinxinData

data_path = '{}/data/data_20170927'.format(PROJECT_ROOT)
sched = BlockingScheduler()

class WinxinSpider():

    output_list = []
    file_data = []
    page_ele_result = {}
    source_file_list = []


    article_url = 'http://data.wxb.com/rankArticle'

    def __init__(self,
                 infile=None,
                 outfile=None,
                 browser_type='chrome',
                 flag_download_data=True,
                 save_db=False,
                 *args, **kwargs):
        self.browser = Browser(browser_type)
        self.infile = infile
        self.outfile = outfile
        self.flag_download_data=flag_download_data
        self.logging = logging
        if not flag_download_data:
            self.data_list = self.preprocess()

    @classmethod
    def generate_cate_url(cls, cate=CATEGORY):
        """
        生成各领域的url
        :param cate:
        :return:
        """
        category_url = OrderedDict()
        for k,v in cate.items():
            category_url[v] = '{}?cate={}'.format(cls.article_url, k)

        return category_url

    def get_next_page(self, page_xpath):
        """
        翻页
        :return:
        """
        next_path = self.browser.find_by_xpath(page_xpath)
        if next_path:
            self.browser.execute_script('window.scrollBy(0,1000)')
            self.browser.find_by_xpath(page_xpath).click()
            time.sleep(random.randint(2,5))
            return True
        else:
            return False

    def get_raw_element(self, cate_url):
        """
        获取当前领域页面的公众号区块元素
        :param category_url:
        :return:
        """
        ele_xpath = '//div[@class="rank-right"]'
        next_page_xpath = '//li[@class="ant-pagination-next"]'

        category_result = []
        try:
            result = self.browser.visit(cate_url, timeout=40)
            if result and 'timeout' in result:
                self.browser.reload()
            element = self.browser.find_by_xpath(ele_xpath).first.html
            category_result.append(element)
            while self.get_next_page(next_page_xpath):
                element = self.browser.find_by_xpath(ele_xpath).first.html
                category_result.append(element)
        except Exception,e:
            self.logging.error(str(e))
            self.browser.quit()

        return category_result


    def preprocess(self):
        """
        数据文件合并
        :return:
        """
        assert os.path.exists(self.infile),'数据文件路径不存在'
        file_names = os.listdir(self.infile)
        if file_names:
            for file_name in file_names:
                if re.search('(P_\d+.txt)',file_name):
                    self.source_file_list.append(file_name)

        total_num = len(self.source_file_list)
        self.logging.info('Total file number ===> %s个' % total_num)

        count = 0
        for file in self.source_file_list:
            fpath = '{}/{}'.format(self.infile, file)
            self.logging.info('正在处理第%s个文件，共%s个. ===> %s' % (count+1, total_num, fpath))
            try:
                data = codecs.open(fpath, 'r', 'gbk').readlines()
                if '字段1' in data[0]:
                    self.file_data.extend(data[1:])
            except UnicodeDecodeError,e:
                self.logging.error('文件{}为非gbk编码.'.format(fpath))
                continue
            count += 1


    def regexp_parse(self, cate_eles=None, save_to_mongo=True):
        """
        解析区块元素或者正则解析网页字符串
        :return:
        """
        self.output_list = []
        if not self.flag_download_data:
            assert self.file_data != []
            cate_results = self.file_data
        else:
            cate_results = cate_eles
            # for cate in cate_eles.values():
            #     cate_results.extend(cate)

        for line in cate_results:
            line_split = re.split(r'\n', line, 1)
            line_left = line_split[0]

            self.logging.info(line_left)

            regexp_title = r'">(\S+)</div><div class="rank-article-table clearfix"'
            matchs = re.findall(regexp_title, line_left, re.S | re.M)

            if matchs:
                category = matchs[0]

                regexp_content = r'<a rel="nofollow" class="title-text" target="_blank" href="(\S+)" data-reactid="\S+">(.*?)</a></div></td><td class="" data-reactid="\S+"><a style="\S+" target="_blank" href="\S+" data-reactid="\S+">(\S+)</a></td>.*?<span class="spread-text" data-reactid="\S+">(\S+)</span></div></div></td>.*?react-text: {1,}\S+ {1,}-->(\S+)<.*?react-text: {1,}\S+ {1,}-->(\S+)<'
                matchs = re.findall(regexp_content, line_left, re.S | re.M)

                if matchs:
                    for item in matchs:
                        match_biz = re.findall(r'.*?biz=(\S+)==&.*?', item[0], re.S | re.M)
                        if match_biz:
                            biz = match_biz[0].replace("%3D", "")
                        else:
                            match_biz = re.findall(r'.*?biz=(\S+)&amp;mid=.*?', item[0], re.S | re.M)
                            if match_biz:
                                biz = match_biz[0].replace("%3D", "")

                        title = item[1]
                        name = item[2]
                        index = item[3]
                        count = item[4]
                        click_count = item[5]

                        line_result = category + '\t' + biz + '\t' + name + '\t' + title + '\t' + index + '\t' + count + '\t' + click_count
                        self.output_list.append(line_result)

                        if save_to_mongo:
                            d = {
                                'host':HOSTNAME,
                                'source':'微信公众号',
                                'category':category,
                                'public_id':biz,
                                'public_name':name,
                                'article_title':title,
                                'spread_index':index,
                                'reading_quantity':count,
                                'point_number':int(click_count),
                            }
                            jprint(d)
                            try:
                                data = WinxinData(**d)
                                query_result = WinxinData.objects.filter(article_title=d["article_title"])
                                if not query_result:
                                    data.save()
                            except Exception,e:
                                self.logging.error(unicode(e))

    @time_deco
    def save_file(self, path):

        try:
            with codecs.open(self.outfile, 'a', encoding='utf-8') as f:
                for line in self.output_list:
                    f.write(line + '\n')
        except Exception,e:
            self.logging.error(unicode(e))


@sched.scheduled_job('interval', hours=3)
def spider_task():

    current_date = datetime.datetime.now().strftime('%Y_%m_%d')

    data_save_dir = "{}/data/articles/{}".format(PROJECT_ROOT, current_date)
    outfile = "{path}/data/articles/{date}/data_{date}.txt".format(path=PROJECT_ROOT, date=current_date)
    visited_url_path = re.sub('.txt','_visited.txt', outfile)
    if not os.path.exists(data_save_dir):
        os.makedirs(data_save_dir)

    if not os.path.exists(visited_url_path):
        f = codecs.open(visited_url_path, 'a', encoding='utf-8')
        f.close()
    else:
        visited_url = codecs.open(visited_url_path, 'r', encoding='utf-8').readlines()
        clean_visited_url = [item.strip('\n') for item in visited_url]

    spider = WinxinSpider(outfile=outfile)
    cate_urls = spider.generate_cate_url()
    for cate_url in cate_urls.values():
        if cate_url not in clean_visited_url:
            result = spider.get_raw_element(cate_url)
            if len(result)>=1:
                spider.regexp_parse(result)
                spider.save_file(outfile)
                with codecs.open(visited_url_path, 'a', encoding='utf-8') as f:
                    f.write(cate_url + '\n')
    spider.browser.quit()



if __name__ == '__main__':

    # sched.start()
    spider_task()
