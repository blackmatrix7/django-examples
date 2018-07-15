#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午11:20
# @Author  : Matrix
# @Site    : 
# @Software: PyCharm
from django.dispatch import receiver
from django.db.models.signals import post_init
from .models import Pizza
from .signals import pizza_done, close_store, open_store

__author__ = 'BlackMatrix'


# sender 指定接收哪个model发出的信号，不加sender的话，会接收到所有的model初始化消息
# dispatch_uid 接收者的唯一
@receiver(post_init, sender=Pizza, dispatch_uid='after_init_model')
def after_init_model(sender, **kwargs):
    print(sender)
    print(kwargs)


# 接受自定义信号
@receiver(pizza_done, dispatch_uid='pizza_done')
def receiver_pizza_done(sender, **kwargs):
    print('pizza done!')
    print(kwargs)


# 接收多个信号
@receiver([open_store, close_store], dispatch_uid='two_signals')
def receiver_pizza_done(sender, **kwargs):
    # 假设有一些开关店前必要的准备
    signal = kwargs['signal']
    # 判断开店还是关店，输出对应的文字
    # 注意传入的signal就是定义的signal
    if signal is open_store:
        print('open_store!')
    elif signal is close_store:
        print('close store!')



if __name__ == '__main__':
    pass
