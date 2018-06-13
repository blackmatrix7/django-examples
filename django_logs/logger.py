#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/5/18 下午2:38
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: logger
# @Software: PyCharm
import logging.config
from django.conf import settings

__author__ = 'blackmatrix'

logger = logging.getLogger('django')
logging.config.dictConfig(settings.LOGGING)


if __name__ == '__main__':
    pass
