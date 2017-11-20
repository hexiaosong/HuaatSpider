# coding: utf-8
"""
Create on 2017/10/19

@author:hexiaosong
"""
from __future__ import unicode_literals

import codecs
import os
import re
from collections import OrderedDict
from data.annotate import (entities_org_list, entities_prd_list, entities_money_list)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


BASEPATH = '/Users/apple/Downloads/entity/brat-v1.3_Crunchy_Frog/data/datasets_2'

def load_file(file_path):
    """
    加载文件拼接成字符串
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        f = codecs.open(file_path, 'r', encoding='utf-8').readlines()
        str_object = ''.join(f)
    else:
        str_object = ''
        print 'File do not exist !!'

    return str_object


def str_len(check_str):
    count = 0
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            count += 1
        else:
            count += 1

    return count


def find_entity(entity,text, cate):
    """
    查找实体,返回实体索引位置
    :param str_object:
    :return:
    """
    lenght = str_len(entity)

    entity_num = 0
    index_position = []

    entity = entity.decode('utf-8')
    if cate in ['org', 'prd']:
        search_res = re.findall(entity, text)

        if search_res:
            entity_num = len(search_res)

        index = -1
        for i in range(entity_num):
            index = text.find(entity, index + 1)
            if entity in ['中国', '农业', '光大', '工商', '民生', '交通', '邮政', '浦发', '招商', '兴业']:
                if text[index + lenght] not in '银行 ':
                    index_position.append((index, index + lenght))
            elif entity in ['平安']:
                if text[(index + lenght):(index + lenght + 2)] not in ' 银行':
                    index_position.append((index, index + lenght))
            elif entity in ['银联']:
                if text[index + lenght] not in '卡':
                    index_position.append((index, index + lenght))
            else:
                index_position.append((index, index + lenght))

    elif cate in ['mon']:
        regexp_list = [
            # '([\d\.]+多*万*W* *元)',
            '(\d[\d\.,]*多*万 *元*)',
            '(\d[\d\.,]* *元)',
            '(\d[\d\.,]*多*W)',
            '(\d[\d\.,]*多*千)',
            '(\d[\d\.]*多* *k)',
            '([\d\.]+多* *块)',
            '([一二三四五六七八九十]+万*元)',
            '([一二三四五六七八九十]+万)',
        ]
        for regexp in regexp_list:
            num = re.compile(regexp).findall(text.decode('utf-8'))
            if num:
                index = -1
                for i in range(len(num)):
                    temp = re.compile(regexp).search(text, index+1)
                    if temp:
                        money = temp.group()
                        start = temp.start()
                        index = temp.end()
                        index_position.append({money:(start, index)})

    return index_position


def generate_ann_doc(entities_dict, text):
    """
    生成标注实体文档
    :param entities:
    :param text:
    :return:
    """
    result = []
    count = 1
    for cate,entity_set in entities_dict.items():
        if cate in ['org', 'prd']:
            for entity in entity_set:
                indexes = find_entity(entity, text, cate)
                if indexes:
                    for index in indexes:
                        if cate == 'org':
                            s = 'T{}\tOrganization {} {}\t{}\n'.format(count,index[0], index[1], entity)
                        elif cate == 'prd':
                            s = 'T{}\tProduct {} {}\t{}\n'.format(count, index[0], index[1], entity)
                        # elif cate == 'mon':
                        #     s = 'T{}\tMoney {} {}\t{}\n'.format(count, index[0], index[1], entity)
                        result.append(s)
                        count += 1
        elif cate in ['mon']:
            indexes = find_entity(entity, text, cate)
            if indexes:
                for item in indexes:
                    s = 'T{}\tMoney {} {}\t{}\n'.format(count, item.values()[0][0], item.values()[0][1], item.keys()[0].decode('utf-8'))
                    result.append(s)
                    count +=1

    return result

def sort_list(list_obj):
    if len(list_obj) == 1:
        return list_obj
    elif len(list_obj) == 2:
        if len(list_obj[0]) < len(list_obj[1]):
            return [list_obj[1], list_obj[0]]
        else:
            return list_obj


def sort_result(s_list):

    T_dict = OrderedDict()
    R_dict = OrderedDict()

    for line in s_list:
        index_num = int(re.search('(\d+)', line[:5]).group(1))
        if 'T' in line[:3]:
            T_dict[line] = index_num
        elif 'R' in line[:3]:
            R_dict[line] = index_num

    sort_T_list = sorted(T_dict.items(), key=lambda item:item[1])
    sort_R_list = sorted(R_dict.items(), key=lambda item: item[1])

    sort_T_list.extend(sort_R_list)
    result = [item[0] for item in sort_T_list]

    return result

def process_ann_file(ann_list):

    combine_result = []
    seq_T_mark = []
    code_T_dict = {}

    seq_R_mark = []
    code_R_dict = {}

    for line in ann_list:
        search_T_result = re.findall('(data\d_[a-z]+_\d+_T\d+)', line)
        search_R_result = re.findall('(data\d_[a-z]+_\d+_R\d+)', line)

        seq_T_mark.extend(search_T_result)
        seq_R_mark.extend(search_R_result)

    uni_seq_T_mark = set(seq_T_mark)
    uni_seq_R_mark = set(seq_R_mark)

    for index_T, mark_T in enumerate(uni_seq_T_mark):
        code_T_dict[mark_T] = index_T+1

    for index_R, mark_R in enumerate(uni_seq_R_mark):
        code_R_dict[mark_R] = index_R+1

    for item in ann_list:
        uni_seq_mark_T_list = re.findall('(data\d_[a-z]+_\d+_T\d+)', item)
        if uni_seq_mark_T_list:
            sort_uni_seq_mark_T_list = sort_list(uni_seq_mark_T_list)
            for mark in sort_uni_seq_mark_T_list:
                item = re.sub('%s' % mark, 'T%s' % code_T_dict[mark], item)

            uni_seq_mark_R_list = re.findall('(data\d_[a-z]+_\d+_R\d+)', item)
            if uni_seq_mark_R_list:
                for mark in uni_seq_mark_R_list:
                    item = re.sub(mark, 'R%s' % code_R_dict[mark], item)
        combine_result.append(item)

    return sort_result(combine_result)



def combine_doc():

    # 分割后的单个文件夹
    dirs = os.listdir(BASEPATH)
    dirs.remove('tmp')
    dirs.remove('.DS_Store')
    dirs.remove('.stats_cache')

    for index, dir in enumerate(dirs):

        print 'Total Document:%s, Processing num is %s.' % (len(dirs), index+1)

        result_text = []
        result_ann = []

        docs = os.listdir(BASEPATH + '/' + dir)  # dir为文件夹  如data1_ann

        txt_docs = [item for item in docs if '.txt' in item]   # txt_docs为文本文件 如data1_aa_1.txt

        for i in range(len(txt_docs)):

            prefix = '{}{}'.format(re.findall('(data\d_[a-z]+_)\d+', txt_docs[0])[0], i+1)

            text = codecs.open('{}/{}/{}.txt'.format(BASEPATH, dir, prefix), 'r', encoding='utf-8').readlines()

            ann = codecs.open('{}/{}/{}.ann'.format(BASEPATH, dir, prefix), 'r', encoding='utf-8').readlines()
            pre_text_len = len(''.join(result_text))

            for line in ann:
                split = line.split('\t')
                split_1 = split[0]
                split_2 = split[1]
                split_3 = split[2]

                new_split_1 = '{}_{}'.format(prefix, split_1)
                if 'T' in split_1:
                    indexes = [int(item) for item in re.findall('(\d+)',split_2)]
                    if 'Organization' in split_2:
                        new_split_2 = 'Organization {} {}'.format(indexes[0]+pre_text_len, indexes[1]+pre_text_len)
                    elif 'Product' in split_2:
                        new_split_2 = 'Product {} {}'.format(indexes[0]+pre_text_len, indexes[1]+pre_text_len)
                    elif 'Money' in split_2:
                        new_split_2 = 'Money {} {}'.format(indexes[0] + pre_text_len, indexes[1] + pre_text_len)
                elif 'R' in split_1:
                    new_split_2 = re.sub('T', '{}_T'.format(prefix), split_2)

                new_line = '{}\t{}\t{}'.format(new_split_1, new_split_2, split_3)
                result_ann.append(new_line)

            result_text.extend(text)

        final_ann_list = process_ann_file(result_ann)

        final_ann_prefix = re.findall('(data\d_[a-z]+)_\d+', txt_docs[0])[0]
        with codecs.open('{}/{}.ann'.format(BASEPATH, final_ann_prefix),'w', encoding='utf-8') as f:
            for item in final_ann_list:
                f.write(item)

    ann_files = [item for item in os.listdir(BASEPATH) if '.ann' in item]

    os.chdir(BASEPATH)
    for ann_file in ann_files:
        os.system('cat %s >> ./tmp/%s' % (ann_file, ann_file))
        os.system('rm %s' % ann_file)




if __name__ == '__main__':

    # for i in 'abcdefg':
    #     res = load_file('/Users/apple/Downloads/brat/brat-v1.3_Crunchy_Frog/data/datasets_1/data1_a%s.txt' % i)
    #     entities = {}
    #     entities['org'] = entities_org_list
    #     entities['prd'] = entities_prd_list
    #     entities['mon'] = entities_money_list
    #     result = generate_ann_doc(entities, res)
    #     with codecs.open('/Users/apple/Downloads/brat/brat-v1.3_Crunchy_Frog/data/datasets_1/data1_a%s.ann' % i, 'w', encoding='utf-8') as f:
    #         for line in result:
    #             f.write(line)
    #
    #     print 'Process Done !'
    # dirs = os.listdir(BASEPATH)
    # dirs.remove('tmp')
    # dirs.remove('.DS_Store')
    # dirs.remove('.stats_cache')
    # for dir in dirs:
    #     path = BASEPATH + '/' + dir
    #     print path
    #
    #     files = os.listdir(path)
    #     txt_files = [item for item in files if '.txt' in item]
    #     for txt in txt_files:
    #         res = load_file(BASEPATH + '/' + dir + '/' + txt)
    #         entities = {}
    #         entities['org'] = entities_org_list
    #         entities['prd'] = entities_prd_list
    #         entities['mon'] = entities_money_list
    #
    #         result = generate_ann_doc(entities, res)
    #
    #         for item in result:
    #             if 'Money' in item:
    #                 print item
    #
    #         ann = txt.split('.')[0]
    #         with codecs.open(BASEPATH + '/' + dir + '/' + ann +'.ann', 'w', encoding='utf-8') as f:
    #             for line in result:
    #                 f.write(line)
    combine_doc()