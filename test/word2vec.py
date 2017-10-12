# coding: utf-8
"""
Create on 2017/10/10

@author:hexiaosong
"""
import codecs
import jieba

infile = 'wiki.zhs.text'
outfile = 'wiki.zh.words.txt'

descsFile = codecs.open(infile, 'rb', encoding='utf-8')

i = 0

with codecs.open(outfile, 'w', encoding='utf-8') as f:
    for line in descsFile:
        i += 1
        if i % 10000 == 0:
            print(i)
        line = line.strip()
        words = jieba.cut(line)
        for word in words:
            f.write(word + ' ')
        f.write('\n')