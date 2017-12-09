# coding: utf-8
"""
Create on 2017/10/30

@author:hexiaosong
"""

from __future__ import unicode_literals

import time
import tornado.ioloop
import tornado.web
from gensim.models import word2vec
from tornado.web import RequestHandler



model_path = '/Users/apple/Documents/packages/word2vec/wiki.zh.text.model'
print 'loading model...'
model = word2vec.Word2Vec.load(model_path)
print 'load model sucessfully !!'


class ExpandHandler(RequestHandler):

    def get(self):
        time_start = time.time()
        keywords = self.get_argument('word')
        topn = int(self.get_argument('topn', 30))

        time_end = time.time()
        try:
            result = model.most_similar(keywords, topn=topn)
        except:
            result = []
        cost_msecs = (time_end - time_start) * 1000

        self.set_header("Content-Type", "application/json")
        self.write({
            'cost': '%fms' % cost_msecs,
            'sim_words_list':result,
            'topn':topn,
        })


# 独立启动的入口函数
def main():
    application = tornado.web.Application([
        (r"/keywords/", ExpandHandler),
    ])
    # 监听端口
    application.listen(8095)
    print 'service start...Demo process please visit http://localhost:8095/keywords/?word=%E4%B9%A0%E8%BF%91%E5%B9%B3&topn=5'
    # 启动服务
    tornado.ioloop.IOLoop.instance().start()


# 独立启动的入口
if __name__ == "__main__":
    main()
