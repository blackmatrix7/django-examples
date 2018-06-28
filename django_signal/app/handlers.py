#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午11:20
# @Author  : Matrix
# @Site    : 
# @Software: PyCharm
from django.dispatch import receiver
from django.db.models.signals import post_init
from .models import Pizza

__author__ = 'BlackMatrix'


# sender 指定接收哪个model发出的信号，不加sender的话，会接收到所有的model初始化消息
# dispatch_uid 接收者的唯一
@receiver(post_init, sender=Pizza, dispatch_uid='after_init_model')
def after_init_model(sender, **kwargs):
    print(sender)
    print(kwargs)


if __name__ == '__main__':
    pass
