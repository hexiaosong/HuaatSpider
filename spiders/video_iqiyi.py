# coding: utf-8
"""
Create on 2017/10/9

@author:hexiaosong
"""
from __future__ import unicode_literals

import os, re, time, random, socket,datetime
from selenium import webdriver
import urllib2
from selenium.common.exceptions import NoSuchElementException
####################
socket.setdefaulttimeout(100)

def openurl(url, head):
    match = re.search(r'^http[s]{0,}://.*', url)
    if match:
        url_tmp = url
    else:
        url_tmp = "http://" + url
    response = urllib2.urlopen(url_tmp)
    # heads = response.getheaders()
    html = response.read()
    response.close()
    return html

def writeDictfile(filename, **dict):
    file = open(filename, 'w',encoding='utf-8')
    for i in dict:
        file.write(i + ":" + dict[i] + "\n")
    file.close()

def time_log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(now + ":" + msg)

def readDictfile(filename):
    import codecs
    file = codecs.open(filename, "r", encoding='gbk').readlines()
    dict_t={}
    for i in file:
        m = re.split(r':', i , 1)
        dict_t[m[0]] = m[1].strip('\n')
    file.close()
    return dict_t

def sleepRandom(b = 5, e = 10, p = "TRUE"):
    t = random.randint(b, e)
    if p:
        time_log("app will sleep" + str(t) + "sec.")
    time.sleep(t)

####################
# print(os.getcwd())
# os.chdir(u"")
# print(os.getcwd())
####################

### Split Data ###
import codecs
data_tmp= codecs.open("/Users/apple/Documents/华院分析/视频/data/iqiyi.txt",'r','utf-8')
data_source=[]
for i in data_tmp:
    data_source.append(i.strip('\n'))
print(len(data_source))

split_num = 20
split_data = [ data_source[i:i+split_num] for i in range(0, len(data_source), split_num) ]

cc=0
for k in split_data:
    with codecs.open(u"/Users/apple/Documents/华院分析/视频/video_source/split_data_%s.txt" % cc, 'w', encoding='utf-8') as file:
        for i in k:
            file.write(i + "\n")
        cc=cc+1
####对数据分割完毕
### Read Data ###
source_path = "/Users/apple/Documents/华院分析/视频/video_source"
source_file_list = []
for fpathe, ddirs, ffs in os.walk(source_path):
    for ff in ffs:
        dmd = re.findall(r'(.*?).txt', ff)
        if dmd:
            source_file_list.append(dmd[0])
print(source_file_list)   # 取得所有分割后的文件名

des_path = u"/Users/apple/Documents/华院分析/视频/video_output"

des_file_list = []
for fpathe, ddirs, ffs in os.walk(des_path):
    for ff in ffs:
        dmd = re.findall(r'output_(.*?).txt', ff)
        des_file_list.append(dmd[0])
print(des_file_list)

driver = webdriver.Chrome()
user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 BIDUBrowser/6.x Safari/537.31',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.44 Safari/537.36 OPR/24.0.1558.25 (Edition Next)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36 OPR/23.0.1522.60 (Edition Campaign 54)'
]
for ff in source_file_list:   # 对分割文件进行遍历
    print(ff)
    sleepRandom(1, 1)
    print("FFFFFFFF")
    file_name = ff + ".txt"
    data_tmp = codecs.open(u"/Users/apple/Documents/华院分析/视频/video_source/" + file_name, encoding='utf-8')
    data = []
    for i in data_tmp:
        data.append(i.strip('\n'))
    print(data)
    print("EEEEEEEEE")

    if ff not in des_file_list:   # 判断当前打开分割文件是否在结果输出文件list中存在
        output_1 = []

        for v in data:
            sleepRandom(2, 4)
            aa = v.split("\t")
            print(aa)
            url = "www.iqiyi.com/" + aa[0] + ".html"
            print(url)

            user_agent = random.choice(user_agents)
            aheaders = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Connection': 'keep-alive',
                        # 'GET': next_url,
                        'User-Agent': user_agent
                        }

            pro_id = aa[0]

            try:
                video_html = openurl(url, aheaders)
                # video_html = video_html.decode('utf-8')
                #print(video_html)

                error=""
                error_part = r'404错误'
                error_matchs = re.findall(error_part, video_html, re.S | re.M)
                if error_matchs:
                    error = error_matchs[0]
                print(error)

                if video_html and error=="":
                    title = ""
                    title_part = r'name="irTitle" content="(.*?)"'
                    title_matchs = re.findall(title_part, video_html, re.S | re.M)
                    if title_matchs:
                        title = title_matchs[0]
                    print(title)

                    desc_name = ""
                    desc_part = r'<a rseat="bread2_4" class="c999" title="\S+" href="(\S+)">'
                    desc_matchs = re.findall(desc_part, video_html, re.S | re.M)
                    if desc_matchs:
                        desc_name = desc_matchs[0]
                        level1_name = ""
                        level1_name_part = r'<a rseat="bread2_3" class="c999" title="(.*?)"'
                        level1_name_matchs = re.findall(level1_name_part, video_html, re.S | re.M)
                        if level1_name_matchs:
                            level1_name = level1_name_matchs[0]
                        print(level1_name)

                        level2_name = ""
                        level2_name_part = r'<a rseat="bread2_4" class="c999" title="(.*?)"'
                        level2_name_matchs = re.findall(level2_name_part, video_html, re.S | re.M)
                        if level2_name_matchs:
                            level2_name = level2_name_matchs[0]
                        print(level2_name)
                    else:
                        desc_part = r'<a rseat="bread2_3" class="c999" title="\S+" href="(\S+)">'
                        desc_matchs = re.findall(desc_part, video_html, re.S | re.M)
                        if desc_matchs:
                            desc_name = desc_matchs[0]
                        level1_name = ""
                        level1_name_part = r'<a rseat="bread2_2" class="c999" title="(.*?)"'
                        level1_name_matchs = re.findall(level1_name_part, video_html, re.S | re.M)
                        if level1_name_matchs:
                            level1_name = level1_name_matchs[0]
                        print(level1_name)

                        level2_name = ""
                        level2_name_part = r'<a rseat="bread2_3" class="c999" title="(.*?)"'
                        level2_name_matchs = re.findall(level2_name_part, video_html, re.S | re.M)
                        if level2_name_matchs:
                            level2_name = level2_name_matchs[0]
                        print(level2_name)
                    print(desc_name)

                    user_agent = random.choice(user_agents)
                    aheaders = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'Connection': 'keep-alive',
                                # 'GET': next_url,
                                'User-Agent': user_agent
                                }

                    pro_id = aa[0]

                    sleepRandom(2, 4)

                    # try:
                    desc_name_html = openurl(desc_name, aheaders)
                    desc_name_html = desc_name_html.decode('utf-8')  # , 'ignore')
                    #print(desc_name_html)

                    num = ""
                    num_part = r'播放量：(.*?)播放量数据'
                    num_matchs = re.findall(num_part, desc_name_html, re.S | re.M)
                    print(num_matchs)
                    if num_matchs:
                        num_part_1 = r'id="widget-playcount">(.*?)</i>'
                        num_matchs_1 = re.findall(num_part_1, num_matchs[0], re.S | re.M)
                        print(num_matchs_1)
                        num = num_matchs_1[0]
                    else:
                        num_part = r'<span class="effrct-PVNum">(.*?)播放</span>'
                        num_matchs = re.findall(num_part, desc_name_html, re.S | re.M)
                        print(num_matchs)
                        if num_matchs:
                            num = num_matchs[0]
                    print(num)

                    if num == "":
                        try:
                            match = re.search(r'^http[s]{0,}://.*', url)
                            if match:
                                url_tmp = url
                            else:
                                url_tmp = "http://" + url

                            print(url_tmp)

                            driver = webdriver.Chrome()
                            driver.set_window_size(1120, 550)
                            driver.get(url_tmp)

                            sleepRandom(4, 4)

                            num_page_tmp = driver.page_source
                            # print(num_page_tmp)

                            num = ""
                            num_part = r'播放：<span.*?>(.*?)</span><b></b>'
                            num_matchs = re.findall(num_part, num_page_tmp, re.S | re.M)
                            if num_matchs:
                                num = num_matchs[0]
                            print(num)

                            driver.close()
                        except:
                            num = ""

                    director = ""
                    director_part = r'导演：(.*?)<p class="progInfo_rtp">'
                    director_matchs = re.findall(director_part, video_html, re.S | re.M)
                    if director_matchs:
                        director_matchs_1 = re.findall(r'title="(.*?)">', director_matchs[0], re.S | re.M)
                        if director_matchs_1:
                            director_tmp = []
                            for i in director_matchs_1:
                                director_tmp.append(i)
                            director = ' '.join(director_tmp)
                    print(director)

                    performer = ""
                    performer_part = r'主演：</span>(.*?)</p>'
                    performer_matchs = re.findall(performer_part, video_html, re.S | re.M)
                    if performer_matchs:
                        performer_matchs_1 = re.findall(r'title="(\S+)">', performer_matchs[0], re.S | re.M)
                        if performer_matchs_1:
                            performer_tmp = []
                            for i in performer_matchs_1:
                                performer_tmp.append(i)
                            performer = ' '.join(performer_tmp)
                    print(performer)

                    year = ""
                    year_part = r'年份：</em>(.*?)</li>'
                    year_matchs = re.findall(year_part, video_html, re.S | re.M)
                    if year_matchs:
                        year_matchs_1 = re.findall(r'<span>(\S+)</span>', year_matchs[0], re.S | re.M)
                        if year_matchs_1:
                            year = year_matchs_1[0]
                    print(year)

                    type = ""
                    type_part = r'类型：</em>(.*?)</li>'
                    type_matchs = re.findall(type_part, video_html, re.S | re.M)
                    if type_matchs:
                        type_matchs_1 = re.findall(r'title="(\S+)"', type_matchs[0], re.S | re.M)
                        if type_matchs_1:
                            type = type_matchs_1[0]
                    else:
                        type_part = r'类型：(.*?)</em> </div>'
                        type_matchs = re.findall(type_part, desc_name_html, re.S | re.M)
                        if type_matchs:
                            type_matchs_1 = re.findall(r'">(\S+)</a>', type_matchs[0], re.S | re.M)
                            if type_matchs_1:
                                type_tmp = []
                                for i in type_matchs_1:
                                    type_tmp.append(i)
                                    type = ' '.join(type_tmp)
                    print(type)

                    area = ""
                    area_part = r'地区：</em>(.*?)</li>'
                    area_matchs = re.findall(area_part, video_html, re.S | re.M)
                    if area_matchs:
                        area_matchs_1 = re.findall(r'title="(\S+)"', area_matchs[0], re.S | re.M)
                        if area_matchs_1:
                            area = area_matchs_1[0]
                    else:
                        area_part = r'地区：(.*?)</em> </div>'
                        area_matchs = re.findall(area_part, desc_name_html, re.S | re.M)
                        if area_matchs:
                            area_matchs_1 = re.findall(r'">(\S+)</a>', area_matchs[0], re.S | re.M)
                            if area_matchs_1:
                                area = area_matchs_1[0]
                    print(area)

                    premiere = ""
                    premiere_part = r'首映：</em>(.*?)</li>'
                    premiere_matchs = re.findall(premiere_part, video_html, re.S | re.M)
                    if premiere_matchs:
                        premiere_matchs_1 = re.findall(r'<span>(\S+)</span>', premiere_matchs[0], re.S | re.M)
                        if premiere_matchs_1:
                            premiere = premiere_matchs_1[0]
                    print(premiere)

                    language = ""
                    language_part = r'语言：</em>(.*?)</li>'
                    language_matchs = re.findall(language_part, video_html, re.S | re.M)
                    if language_matchs:
                        language_matchs_1 = re.findall(r'>(\S+)</span>', language_matchs[0], re.S | re.M)
                        if language_matchs_1:
                            language = language_matchs_1[0]
                    else:
                        language_part = r'语言：(.*?)</em> </div>'
                        language_matchs = re.findall(language_part, desc_name_html, re.S | re.M)
                        if language_matchs:
                            language_matchs_1 = re.findall(r'">(\S+)</a>', language_matchs[0], re.S | re.M)
                            if language_matchs_1:
                                language = language_matchs_1[0]
                    print(language)

                    output_1.append("1" +'\t'+ "爱奇艺" +'\t'+ pro_id +"\t"+ level1_name +"\t"+ level2_name +"\t"+ title +"\t"+ num +"\t"+ director +"\t"+ performer +"\t"+ year +"\t"+ type +"\t"+ area +"\t"+ premiere +"\t"+ language)
                    print(output_1)

            except:
                output_1.append("1" + '\t' + "爱奇艺" + '\t' + pro_id + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error" + "\t" + "404error")
                print(output_1)
                sleepRandom(4, 6)


        file = open("video_output/output_%s.txt" % ff, 'w', encoding='utf-8')
        for i in output_1:
            file.writelines(i + "\n")
        file.close()


print("==================================")
time_log("_____" + "EEEEEEEEE_End")