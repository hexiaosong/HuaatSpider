# coding: utf-8
"""
Create on 2017-09-27 

@author:hexiaosong
"""

from __future__ import  unicode_literals

import re
import time
import datetime
import codecs
from spiders import *

data_path = '{}/data/data_20170927'.format(PROJECT_ROOT)

def time_deco(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        delta_time = end_time - start_time
        print '%s costs time : %f s' % (func.__name__, delta_time)
    return wrapper

class WinxinSpider():

    output_list = []
    source_file_list = []
    file_data = []

    def __init__(self, infile=data_path, outfile=None):
        self.infile = infile
        self.outfile = outfile
        self.logging = logging
        self.data_list = self.preprocess()

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
        logging.info('Total file number ===> %s个' % total_num)

        count = 0
        for file in self.source_file_list:
            fpath = '{}/{}'.format(data_path,file)
            logging.info('正在处理第%s个文件，共%s个. ===> %s' % (count+1, total_num, fpath))
            try:
                data = codecs.open(fpath, 'r', 'gbk').readlines()
                if '字段1' in data[0]:
                    self.file_data.extend(data[1:])
            except UnicodeDecodeError,e:
                logging.error('文件{}为非gbk编码.'.format(fpath))
                continue
            count += 1


    def regexp_parse(self):
        """
        正则解析网页字符串
        :return:
        """
        assert self.file_data != []
        for line in self.file_data:
            line_split = re.split(r'\n', line, 1)
            line_left = line_split[0]

            logging.info(line_left)

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

    @time_deco
    def save_file(self):

        if os.path.exists(self.outfile):
            self.outfile = "{}/data/data_{}.txt".format(PROJECT_ROOT, datetime.datetime.now().strftime('%Y_%m_%d'))
            logging.debug('无输出文件路径，数据保存为默认路径:%s' % self.outfile)
        try:
            with codecs.open(self.outfile, 'w', encoding='utf-8') as f:
                for line in self.output_list:
                    f.write(line + '\n')
        except Exception,e:
            logging.error(e)


if __name__ == '__main__':

    infile = data_path
    outfile = '/Users/apple/Downloads/data_20170927.txt'
    spider = WinxinSpider(infile=data_path, outfile=outfile)
    spider.regexp_parse()
    spider.save_file()
