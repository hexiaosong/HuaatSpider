# coding: utf-8
"""
Create on 2017-09-27

@author:hexiaosong
"""

import os
from os.path import dirname
import logging

PROJECT_ROOT = dirname(dirname(os.path.abspath(__file__))).replace('\\', '/')

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
