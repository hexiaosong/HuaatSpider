# coding: utf-8
"""
Create on 2017/10/12

@author:hexiaosong
"""
import re
import requests
from bs4 import BeautifulSoup
from utils.common import jprint


def get_html(url):
    """
    获取网页
    :param url:
    :return:
    """
    html = ''
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            html = resp.content
    except Exception,e:
        print 'Error: %s !' % str(e)

    return html


def extract_html(html=None):
    """
    抽取网页文本
    :param html:
    :return:
    """
    if not html:
        return ''

    weixin_name = clean_content = title = ''

    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    html = html.decode('utf-8')
    soup = BeautifulSoup(html)

    _ = [script.extract() for script in soup.findAll('script')]
    _ = [style.extract() for style in soup.findAll('style')]

    elements = soup.findAll('div', {"id":"img-content"})
    title_eles = soup.findAll('h2', {"class":"rich_media_title"})
    name_eles = soup.findAll('span', {"class": "profile_meta_value"})

    if elements:
        element = elements[0]
        content = element.get_text()
        clean_content = re.sub('[ \n\r]','', content)

    if name_eles:
        name_element = name_eles[0]
        weixin_name = name_element.get_text()

    if title_eles:
        title_element = title_eles[0]
        title = title_element.get_text()
        title = re.sub('[ \n\r]','', title)

    d = {
        "weixin_name": weixin_name,
        "clean_content": clean_content,
        "article_title":title
    }
    return d

if __name__ == '__main__':

    url = 'http://mp.weixin.qq.com/s?src=11&timestamp=1507858764&ver=449&signature=AXydSQXOjnhG6Un9URPB99DEILKwTIUts0mKsIxLgXQepId4GbrGhc9ZWojBCf1OEKv2xmkTAq8LzfV1xwDeJmCP2yN32zF-g4OCP0K7szyF5ONRVwAnMCtSvEovQJfB&new=1'
    html = get_html(url)

    result = extract_html(html)
    tail_str = u'赞赏长按二维码向我转账受苹果公司新规定影响，微信iOS版的赞赏功能被关闭，可通过二维码转账支持公众号。'
    jprint(result)