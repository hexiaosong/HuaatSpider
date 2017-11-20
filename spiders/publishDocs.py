# coding: utf-8
"""
Create on 2017/10/27

@author:hexiaosong
"""
from __future__ import  unicode_literals

import re
import codecs
import xlrd
import time
from collections import OrderedDict
from splinter import Browser
from spiders import *
from utils.common import jprint

COUNT = 0

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')

excel_path = '{}/spiders/data/'.format(PROJECT_ROOT)


def transform_dict(list_obj):
    """
    将excel行信息转化为dict
    :param list_obj:
    :return:
    """
    assert isinstance(list_obj, list)
    if len(list_obj)==6:
        d = {
            "areaCode":list_obj[0],
            "address": list_obj[1],
            "account":list_obj[2],
            "merchant":list_obj[3],
            "phone":list_obj[4],
            "contacts":list_obj[5],
        }
    else:
        d = {}
    return d



def get_excel_data(path):

    result = []
    assert os.path.isfile(path)
    logging.info(path)
    data = xlrd.open_workbook(path)

    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols

    for i in range(nrows-1):
        row_data = [unicode(item).split('.')[0] for item in table.row_values(i + 1)]
        result.append(row_data)

    for item in result:
        print '\t'.join(item)
    logging.info('数据共{}行, {}列.'.format(nrows, ncols))

    return result


def split_area(area_str):
    split_result = area_str.split('-')
    if len(split_result) == 3:
        d = {
            'province':split_result[0].strip(),
            'city':split_result[1].strip(),
            'area':split_result[2].strip(),
        }
        return d
    else:
        return {}


def is_login(browser):

    if '统计报表' in browser.html:
        return True
    else:
        return False


def login(username='hbcdadmin', password='chengduyy', captcha_code='aa' ,browser_type='chrome'):

    login_url = 'http://hbfq.huaat.com'

    b = Browser(browser_type)
    b.visit(login_url)

    b.find_by_xpath('//input[@id="username"]').fill(username)
    b.find_by_xpath('//input[@name="password"]').fill(password)
    b.find_by_xpath('//input[@id="validInput"]').fill(captcha_code)

    time.sleep(1)
    b.find_by_xpath('//button[@id="loginBtn"]').click()

    time.sleep(6)
    if is_login(b):
        logging.info('登录成功！')
        return b
    else:
        logging.info('网站响应超时！')
        b.quit()




def choose_date(b):

    b.find_by_xpath('//*[@id="queryTime"]').click()
    # if COUNT < 1:
    #     b.find_by_xpath('/html/body/div[3]/div[4]/div/table/thead/tr[1]/th[2]/select[2]').click()
    #     time.sleep(1)
    #     b.find_by_text('2016').first.click()
    #     b.find_by_xpath('/html/body/div[3]/div[4]/div/table/tbody/tr[1]/td[7]').click()
    #     b.find_by_xpath('/html/body/div[3]/div[1]/div/button[1]').click()
    # else:
    ele = b.find_by_xpath('//div[@class="daterangepicker dropdown-menu show-calendar opensright"]')
    div_num = len(ele)
    b.find_by_xpath('/html/body/div[%s]/div[4]/div/table/thead/tr[1]/th[2]/select[2]/option[50]' % (div_num + 2)).click()
    b.find_by_xpath('/html/body/div[%s]/div[4]/div/table/tbody/tr[1]/td[7]' % (div_num + 2)).click()
    b.find_by_xpath('/html/body/div[%s]/div[1]/div/button[1]' % (div_num + 2)).click()


def choose_area(b, area_dict):

    #省份
    b.find_by_text(area_dict.get('province')).click()
    time.sleep(1)
    #市
    b.find_by_text(area_dict.get('city')).click()
    time.sleep(1)
    #区
    b.find_by_text(area_dict.get('area')).click()


def publish_docs(b, data=None):

    global COUNT

    if not is_login(b):
        login()
    if COUNT < 1:
        b.find_by_text(u'商户管理').click()
        COUNT += 1
    time.sleep(3)
    b.find_by_xpath('/html/body/div[2]/div[2]/div/ul/li[4]/ul/li[2]/a/span').click()


    time.sleep(10)
    if b.is_element_present_by_xpath('//*[@id="userTable"]/tbody'):
        logging.info('已跳转至商户管理搜索页面...')
    else:
        b.find_by_xpath('/html/body/div[2]/div[2]/div/ul/li[4]/ul/li[2]/a/span').click()


    choose_date(b)

    b.find_by_xpath('//input[@id="userName"]').fill(data.get("account"))
    b.find_by_xpath('//button[@id="searchUserBtn"]').click()
    time.sleep(3)
    ele = b.find_by_xpath('//*[@id="userTable"]/tbody/tr')

    if len(ele) >= 1:
        b.find_by_xpath('//*[@id="userTable"]/tbody/tr/td[4]/div/span').click()
        time.sleep(3)
        b.find_by_xpath('//button[contains(text(),"添加")]').click()
        time.sleep(3)
        area_dict = split_area(data.get("address"))

        choose_area(b, area_dict)

        # 门店名称
        b.find_by_xpath('//*[@id="shopForm"]/div[3]/div/input[@name="shopName"]').fill(data.get('merchant'))
        # 门店联系人
        b.find_by_xpath('//*[@id="shopForm"]/div[4]/div/input[@name="shopContacter"]').fill(data.get('contacts'))
        # 门店联系人电话
        b.find_by_xpath('//*[@id="shopForm"]/div[5]/div/input[@name="shopContacterNum"]').fill(data.get('phone'))
        # 门店地址
        b.find_by_xpath('//*[@id="shopForm"]/div[6]/div/input').fill(data.get('merchant'))

        # 保存
        b.find_by_xpath('//*[@id="shopForm"]/div[7]/button[1]').click()
        time.sleep(2)
        if data.get("merchant") in b.html:
            logging.info('商户信息已经录入到系统中 ===> {}, {}'.format(data.get('merchant'), data.get('contacts')))
            return True
    else:
        logging.info('商户账号信息未查询结果. {}, {}'.format(data.get('merchant'), data.get('contacts')))


if __name__ == '__main__':

    path = excel_path + '20171031.xlsx'
    result_save_path = re.sub('.xlsx','.txt', path)
    if os.path.exists(result_save_path):
        saved_result = codecs.open(result_save_path, 'r', 'utf-8').readlines()
        clean_saved_result = [item.replace('\n', '').strip() for item in saved_result]
    else:
        clean_saved_result = []
    data = get_excel_data(path)
    data_dict = OrderedDict()
    for item in data:
        data_dict[item[2]] = transform_dict(item)
    b = login()
    if b:
        for key, value in data_dict.items():
            if key not in clean_saved_result:
                publish_docs(b, data=value)
                with codecs.open(result_save_path, 'a', encoding='utf-8') as f:
                    f.write(key + '\n')
            else:
                logging.info("此商户信息已经录入系统. {}, {}".format(key, value.get("merchant")))
    b.quit()