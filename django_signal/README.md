# Django Signal 入门

Django Signal包含一个信号分配者。当框架内发生某些操作时，

[TOC]

## 内建的Signal

> https://docs.djangoproject.com/en/2.0/ref/signals/

**pre_init**

django.db.models.signals.pre_init

创建model时，在`__init__()`方法开始执行时发送

**post_init**

django.db.models.signals.post_init

创建model时，在`__init__()`方法执行完成后发送

**pre_save**

django.db.models.signals.pre_save

在model的`save()`方法开始执行时发送

**post_save**

django.db.models.signals.post_save

在model的`save()`方法执行后发送

**pre_delete**

django.db.models.signals.pre_delete

在model或queryset的`delete()`方法执行时发送

**post_delete**

django.db.models.signals.post_delete

在model或queryset的`delete()`方法执行后发送

**m2m_changed**

django.db.models.signals.m2m_changed

many to many 关系

**class_prepared**

django.db.models.signals.class_prepared

在model定义和注册到Django时发送，Django内部使用，一般不用于第三方程序

**request_started**

django.core.signals.request_started

HTTP 请求之前发送信号

**request_finished**

django.core.signals.request_finished

HTTP 应答之后发送信号

**got_request_exception**

django.core.signals.got_request_exception

HTTP请求出现异常时发送信号

## 自定义Signal

