#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/28 上午10:43
# @Author  : Matrix
# @Site    : 
# @Software: PyCharm
from django.dispatch import Signal

__author__ = 'BlackMatrix'

pizza_done = Signal(providing_args=['toppings', 'size'])


if __name__ == '__main__':
    pass
