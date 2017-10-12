# coding: utf-8
"""
Create on 2017/10/9

@author:hexiaosong
"""
from __future__ import unicode_literals

from utils.common import jprint
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
        url_tmp = "https://" + url
    from splinter import Browser
    b = Browser('chrome')
    html = b.visit()
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
        dict_t[m[0]] = m[1].replace('\r','').strip('\n')
    return dict_t

def sleepRandom(b = 5, e = 10, p = "TRUE"):
    t = random.randint(b, e)
    if p:
        time_log("app will sleep" + str(t) + "sec.")
    time.sleep(t)

####################
#print(os.getcwd())
# os.chdir("C:/ttt")
#print(os.getcwd())
####################
city_url_path = u"/Users/apple/Documents/华院分析/房產/二手房/city/output/anjuke_city.txt"
data = readDictfile(city_url_path)

#des_path = "D:/python_test/URL"
des_path = "/Users/apple/Documents/华院分析/房產/二手房/city/output"

des_file_list = []
for fpathe, ddirs, ffs in os.walk(des_path):
    for ff in ffs:
        dmd = re.findall(r'output_(.*?).txt', ff)
        if dmd:
            des_file_list.append(dmd[0])
print(des_file_list)

print("==================================")

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 BIDUBrowser/6.x Safari/537.31',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.44 Safari/537.36 OPR/24.0.1558.25 (Edition Next)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36 OPR/23.0.1522.60 (Edition Campaign 54)'
]
address=""
for url in data:
    city = data[url]

    if city not in des_file_list:
        time_log("_____" + city + "____SSSSSSS")
        dict_next_page = {}
        next_url = url
        if city=="吴江" or city=="苏州":
            next_url = "http://suzhou.anjuke.com/sale/"
        if city == "无锡":
            next_url = "http://wuxi.anjuke.com/sale/"
        next_page = {}
        output = {}
        output_1 = []
        error_output = {}

        while next_url != "NO":
            sleepRandom(2,2)
            print(next_url)

            user_agent = random.choice(user_agents)
            aheaders = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                         'Connection': 'keep-alive',
                         #'GET': next_url,
                         'User-Agent': user_agent
                        }
            try:
                html = openurl(next_url, aheaders)
                html = html.decode('utf-8')

                part = r'没有符合要求的房源'
                matchs_no = re.findall(part, html, re.S | re.M)
                print(matchs_no)
                if len(matchs_no)<1:
                    part = r'href="(\S+)" target=\'_blank\' class="houseListTitle ">'
                    matchs = re.findall(part, html, re.S | re.M)

                    for match in matchs:
                        sleepRandom(2,4)
                        url_tmp =  match
                        print(url_tmp)
                        print("GGGGGGGGGGGGGG")
                        user_agent = random.choice(user_agents)
                        aheaders = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Connection': 'keep-alive',
                                    # 'GET': next_url,
                                    'User-Agent': user_agent
                                    }
                        try:
                            next_html = openurl(url_tmp, aheaders)
                            next_html = next_html.decode('utf-8')

                            code=""
                            code_part = r'prop/view/(.*?)\?'
                            code_matchs = re.findall(code_part, match, re.S | re.M)
                            if len(code_matchs) > 0:
                                code = code_matchs[0]
                            print(code)

                            title=""
                            title_part = r'<title>(.*?)</title>'
                            title_matchs = re.findall(title_part, next_html, re.S | re.M)
                            if len(title_matchs) > 0:
                                title = title_matchs[0]
                            print(title)

                            price=""
                            price_part = r'<span class="light info-tag"><em>(.*?)</em>万</span>'
                            price_matchs = re.findall(price_part, next_html, re.S | re.M)
                            if len(price_matchs) > 0:
                                price = price_matchs[0]
                            print(price)

                            unitprice=""
                            unitprice_part = r'<dl><dt>房屋单价：</dt><dd>(.*?) 元/m²</dd></dl>'
                            unitprice_matchs = re.findall(unitprice_part, next_html, re.S | re.M)
                            if len(unitprice_matchs) > 0:
                                unitprice = unitprice_matchs[0]
                            print(unitprice)

                            downpay=""
                            downpay_part = r'<dl><dt>参考首付：</dt><dd>\n\t{1,}(.*?)\t{1,}<i class="iconfont i-calculator">'
                            downpay_matchs = re.findall(downpay_part, next_html, re.S | re.M)
                            if len(downpay_matchs) > 0:
                                downpay = downpay_matchs[0]
                            else:
                                downpay_part = r'<dl><dt>参考首付：</dt><dd>\n {1,}(.*?)万 {1,}<i class="iconfont i-calculator">'
                                downpay_matchs = re.findall(downpay_part, next_html, re.S | re.M)
                                if len(downpay_matchs) > 0:
                                    downpay = downpay_matchs[0]
                            print(downpay)

                            monpay=""

                            design=""
                            design_part = r'<dl><dt>房型：</dt><dd>\n\t{1,}(.*?)\n\t{1,}(.*?)\n\t{1,}(.*?)\n\t{1,}</dd></dl>'
                            design_matchs = re.findall(design_part, next_html, re.S | re.M)
                            if len(design_matchs) > 0:
                                design = design_matchs[0][0]+design_matchs[0][1]+design_matchs[0][2]
                            else:
                                design_part = r'<dl><dt>房型：</dt><dd>\n {1,}(.*?)\n {1,}(.*?)\n {1,}(.*?)\n {1,}</dd></dl>\n'
                                design_matchs = re.findall(design_part, next_html, re.S | re.M)
                                if len(design_matchs) > 0:
                                    design = design_matchs[0][0]+design_matchs[0][1]+design_matchs[0][2]
                            print(design)

                            area=""
                            area_part = r'<dl><dt>面积：</dt><dd>(.*?)平方米</dd></dl>'
                            area_matchs = re.findall(area_part, next_html, re.S | re.M)
                            if len(area_matchs) > 0:
                                area = area_matchs[0]
                            print(area)

                            floor=""
                            floor_part = r'<dl><dt>楼层：</dt><dd>(\S+)(.*?)</dd></dl>'
                            floor_matchs = re.findall(floor_part, next_html, re.S | re.M)
                            if len(floor_matchs) > 0:
                                floor = floor_matchs[0][0]
                            print(floor)

                            orientations=""
                            orientations_part = r'<dl><dt>朝向：</dt><dd>(.*?)</dd></dl>'
                            orientations_matchs = re.findall(orientations_part, next_html, re.S | re.M)
                            if len(orientations_matchs) > 0:
                                orientations = orientations_matchs[0]
                            print(orientations)

                            decoration=""
                            decoration_part = r'<dl><dt>装修程度：</dt><dd>(.*?)</dd></dl>'
                            decoration_matchs = re.findall(decoration_part, next_html, re.S | re.M)
                            if len(decoration_matchs) > 0:
                                decoration = decoration_matchs[0]
                            print(decoration)

                            age=""
                            age_part = r'<dl><dt>年代：</dt><dd>(.*?)</dd></dl>'
                            age_matchs = re.findall(age_part, next_html, re.S | re.M)
                            if len(age_matchs) > 0:
                                age = age_matchs[0]
                            print(age)

                            type=""
                            type_part = r'<dl><dt>类型：</dt><dd>(.*?)</dd></dl>'
                            type_matchs = re.findall(type_part, next_html, re.S | re.M)
                            if len(type_matchs) > 0:
                                type = type_matchs[0]
                            print(type)

                            village=""

                            keyword=""
                            keyword_part = r'<a href="javascript:">(\S+)</a>'
                            keyword_matchs = re.findall(keyword_part, next_html, re.S | re.M)
                            if len(keyword_matchs) > 0:
                                for ee in keyword_matchs:
                                    if len(keyword) > 0:
                                        keyword = ee + "," + keyword
                                    else:
                                        keyword = ee
                            print(keyword)

                            #output[url_tmp] ="1"+'\t'+"anjuke"+ '\t'+ city+'\tcode='+code+'\ttitle='+title+'\tprice='+price+'\tunitprice='+unitprice+'\tdownpay='+downpay+'\tmonpay='+monpay+'\tdesign='+design+'\tarea='+area+'\tage='+age+'\torientations='+orientations+'\tfloor='+floor+'\tdecoration='+decoration+'\ttype='+type+'\tvillage='+village+'\taddress='+address
                            #print(output)
                            output_1.append("4" + '\t' + "anjuke" + '\t' + city + '\t' + code + '\t' + title + '\t' + price + '\t' + unitprice + '\t' + downpay + '\t' + monpay + '\t' + design + '\t' + area + '\t' + age + '\t' + orientations + '\t' + floor + '\t' + decoration + '\t' + type + '\t' + village + '\t' + address + '\t' + keyword)
                            print(output_1)
                        except:
                            error_output[next_url] = url_tmp
                            print(error_output)
                            print("PPPPPPPPPPPPP")
            except:
                error_output[next_url] = url_tmp
                print("NNNNNNNNNnn")
                #print(error_output)
            part_next_page = r'<a href="(\S+)" class="aNxt">下一页 &gt;</a>'
            next_match = re.findall(part_next_page, html, re.S | re.M)
            #print(next_match)
            if len(next_match) > 0:
                next_url = next_match[0]
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
            else:
                next_url="NO"
        if len(error_output) > 0:
           writeDictfile("output_error/output_%s.txt" % city, **error_output)
        #writeDictfile("output/output_%s.txt" % city, **output)
        file = open("output_1/output_%s.txt" % city, 'w', encoding='utf-8')
        for i in output_1:
            file.writelines(i + "\n")
        file.close()
        time_log("__"+ city +"__"+ "EEEEEEEEE_End")
        print("@@@@@@@@@@@@@@@@@@@@@@@")

