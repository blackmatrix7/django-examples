#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午11:20
# @Author  : Matrix
# @Site    : 
# @Software: PyCharm
from django.dispatch import receiver
from django.db.models.signals import post_init
from .models import Article

__author__ = 'BlackMatrix'


@receiver(post_init, sender=Article, dispatch_uid='after_init_model')
def after_init_model(sender, **kwargs):
    print(sender)
    print(kwargs)


if __name__ == '__main__':
    pass
