# coding: utf-8
"""
Create on 2017/10/13

@author:hexiaosong
"""
import base64
import hashlib
import json
import urllib

import requests


def md5str(str):
    # md5加密字符串

    m = hashlib.md5(str.encode(encoding="utf-8"))
    return m.hexdigest()


def md5(byte):
    # md5加密byte
    return hashlib.md5(byte).hexdigest()


class DamatuAPI(object):
    """

    """
    ID = '51246'
    KEY = 'b5b398ac4c8ae43413baae51934a8906'
    HOST = 'http://api.dama2.com:7766/app/'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_sign(self, param=b''):
        """

        :param param:
        :return:
        """
        x = bytes(self.KEY).encode(encoding="utf-8")
        y = bytes(self.username).encode(encoding="utf-8")
        return md5(x + y + param)[:8]

    def get_password(self):
        """

        :return:
        """
        return md5str(self.KEY + md5str(md5str(self.username) + md5str(self.password)))

    def get_balance(self):
        # 查询余额 return 是正数为余额 如果为负数 则为错误码
        data = {
            'appID': self.ID,
            'user': self.username,
            'pwd': dmt.get_password(),
            'sign': dmt.get_sign()
        }
        url = self.HOST + 'd2Balance'
        res = requests.get(url, data)
        jres = res.json()

        if jres['ret'] == 0:
            return jres['balance']
        else:
            return jres['ret']

    def decode(self, file_path, type):
        """
         # 报错 参数id(string类型)由上传打码函数的结果获得 return 0为成功 其他见错误码
        :param filePath:
        :param type: 需要识别的图片类型编码,如: 302 是 4汉字点击,返回坐标
        :return:
        """
        f = open(file_path, 'rb')
        fdata = f.read()
        filedata = base64.b64encode(fdata)
        f.close()
        data = {
            'appID': self.ID,
            'user': self.username,
            'pwd': dmt.get_password(),
            'type': type,
            'fileDataBase64': filedata,
            'sign': dmt.get_sign(fdata)
        }
        res = requests.post(self.HOST + 'd2File', data)
        jres = res.json()
        print("打码兔返回结果: {}".format(jres))

        return jres

        # if jres['ret'] == 0:
        #     # 注意这个json里面有ret，id，result，cookie，根据自己的需要获取
        #     return jres['result']
        # else:
        #     return jres['ret']

    def decode_url(self, url, type):
        """
        # url地址打码 参数 url地址  type是类型(类型查看http://wiki.dama2.com/index.php?n=ApiDoc.Pricedesc)
        return 是答案为成功 如果为负数 则为错误码
        :param url:
        :param type:
        :return:
        """
        data = {
            'appID': self.ID,
            'user': self.username,
            'pwd': dmt.getPwd(),
            'type': type,
            'url': urllib.parse.quote(url),
            'sign': dmt.getSign(url.encode(encoding="utf-8"))
        }
        res = requests.get('d2Url', data)
        res = str(res, encoding="utf-8")
        jres = json.loads(res)
        print(jres)

        if jres['ret'] == 0:
            # 注意这个json里面有ret，id，result，cookie，根据自己的需要获取
            return jres['result']
        else:
            return jres['ret']


    def report_error(self, id):
        """
         # 报错 参数id(string类型)由上传打码函数的结果获得 return 0为成功 其他见错误码
        :param id:
        :return:
        """

        data = {
            'appID': self.ID,
            'user': self.username,
            'pwd': dmt.getPwd(),
            'id': id,
            'sign': dmt.getSign(id.encode(encoding="utf-8"))
        }
        url = self.HOST + 'd2ReportError'
        res = requests.get(url, data)
        res = str(res, encoding="utf-8")
        jres = json.loads(res)
        return jres['ret']


dmt = DamatuAPI("test", "test")
# 调用类型实例：
# 1.实例化类型 参数是打码兔用户账号和密码
# dmt = DamatuAPI("likaiguo", "lkg123456")
# 2.调用方法：
# print(u"打码兔余额: %s" % dmt.get_balance())  # 查询余额

if __name__ == '__main__':
    # print(dmt.decode('zhilian-1.png',302)) #智联3汉字点击
    # {'ret': 0, 'sign': '89302cd6', 'result': '115,111|241,128|152,143', 'id': 142331542}
    # print(dmt.decode('zhilian-weixinhao.png',302))
    # {'result': '45,127|92,83|200,89|130,128', 'id': 152619966, 'ret': 0, 'sign': 'df40e06b'}

    # print(dmt.decode('liepin-1.png',302)) #liepin 4汉字点击
    # {'ret': 0, 'sign': '7452c4d0', 'result': '119,155|156,122|82,125|55,158', 'id': 142183547}

    # print(dmt.decode('0349.bmp',200)) #上传打码
    # print(dmt.decodeUrl('http://captcha.qq.com/getimage?aid=549000912&r=0.7257105156128585&uin=3056517021',200)) #上传打码
    # print(dmt.reportError('894657096')) #上报错误

    # print(dmt.get_balance())  # 查询余额
    # print(dmt.decode('/Users/likaiguo/github/resumeSpider/images/zhilian_spider_2017-01-16_15:11:49_OG_R32.png',302))
    # print(dmt.decode('/Users/likaiguo/github/resumeSpider/images/zhilian_spider_2017-01-16_15:24:36_JvW1n8.png',302))
    # print(dmt.decode('/Users/likaiguo/github/resumeSpider/images/zhilian_spider_2017-01-16_15:23:01_ptWpSF.png', 302))

    # 验证码识别错误,返回error
    # print (dmt.decode('/Users/apple/github/resumeSpider/images/zhilian_spider_2017-03-31_23:28:21_7zDJma.png', 302))
    # print(dmt.get_balance())  # 查询余额
    # {u'sign': u'261c86bf', u'id': 807630025, u'ret': 0, u'result': u'ERROR'}
    # error 表示打码员认为不是一个验证码

    dmt = DamatuAPI("test", "test")
    result = dmt.decode('/Users/apple/Downloads/000UoZbwv.png', 44).get('result')
    # print dmt.decode_url('http://captcha.qq.com/getimage?aid=549000912&r=0.7257105156128585&uin=3056517021', 200) # 上传打码

