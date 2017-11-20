# coding: utf-8
"""
Create on 2017/10/19

@author:hexiaosong
"""
from __future__ import division
import codecs
import os
import math
import shutil


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

BASEPATH = '/Users/apple/Downloads/entity/brat-v1.3_Crunchy_Frog/data/datasets_1'

def get_txt_files(path):

    assert os.path.exists(path)

    files = os.listdir(path)
    txt_files = [f for f in files if '.txt' in f]

    return txt_files


def split_single_file(file_name, text_list):

    file_num = int(math.ceil(len(text_list)/10))
    line_count = 0
    file_name = file_name.replace('.txt','')
    os.mkdir('{}/{}'.format(BASEPATH, file_name))
    for num in range(file_num):
        if len(text_list)-num*10 >= 10:
            with codecs.open('{}/{}/{}_{}.txt'.format(BASEPATH, file_name,file_name, num+1), 'w', encoding='utf-8') as f:
                for text in text_list[line_count:10*(num+1)]:
                    f.write(text)
                ann_file = open('{}/{}/{}_{}.ann'.format(BASEPATH, file_name,file_name, num+1),'w')
                ann_file.close()
                line_count += 10

        elif len(text_list)-num*10 >0 and len(text_list)-num*10 < 10:
            with codecs.open('{}/{}/{}_{}.txt'.format(BASEPATH, file_name, file_name, num), 'w', encoding='utf-8') as f:
                for text in text_list[line_count*10:]:
                    f.write(text)
                ann_file = open('{}/{}/{}_{}.ann'.format(BASEPATH, file_name, file_name, num),'w')
                ann_file.close()
                line_count += 10

def move_conf_file():
    file_name = ['annotation.conf', 'tools.conf', 'visual.conf']
    for file in file_name:
        file_path = BASEPATH + '/' + file
        docs = os.listdir(BASEPATH)
        dirs = [doc for doc in docs if 'data' in doc]
        for dir in dirs:
            dir_path = BASEPATH + '/' + dir
            shutil.copy(file_path, dir_path)




if __name__ == '__main__':

    # text_files = get_txt_files(BASEPATH+'/tmp')
    # for file in text_files:
    #     text_list = codecs.open('{}/tmp/{}'.format(BASEPATH, file), 'r').readlines()
    #     split_single_file(file, text_list)
    move_conf_file()