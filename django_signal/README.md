# Django Signal 入门

Django Signal包含一个信号分配者。当框架内发生某些操作时，

[TOC]

## 内建的Signal

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

除内置信号外，还可以自定义型号是Singal对象的实例。

signals.py

```
from django.dispatch import Signal
pizza_done = Signal(providing_args=['toppings', 'size'])
```

上面的例子，定义一个pizza_done的型号，接受两个参数：toppings、size。

## 监听信号

我们还需要定义receiver，用于接受型号，并执行一些操作。

### 监听内置信号

对于Django内置的信号，只需要定义receiver即可。

receivers.py

```python
from django.dispatch import receiver
from django.db.models.signals import post_init

# post_init指定接受model开始初始化的信号
# sender 指定接收哪个model发出的信号，不加sender的话，会接收到所有的model初始化消息
# dispatch_uid 保证接收者的唯一
@receiver(post_init, sender=Pizza, dispatch_uid='after_init_model')
def after_init_model(sender, **kwargs):
    print(sender)
    print(kwargs)
```

### 监听自定义信号

监听自定义的信号时，同样需要定义receiver。

通监听内置信号一样，使用receiver装饰器，设定需要监听的信号，及通过dispatch_uid保证接受者的唯一

```python
from django.dispatch import receiver
from .signals import pizza_done

# 接受自定义信号
@receiver(pizza_done, dispatch_uid='pizza_done')
def receiver_pizza_done(sender, **kwargs):
    print('pizza donen!')
    print(kwargs)
```

### 监听多个信号

receiver可以同时监听多个信号，假如我们需要同时监听post_init和pizza_done两个信号

```python
from django.dispatch import receiver
from django.db.models.signals import post_init
from .signals import pizza_done

# 接受自定义信号
@receiver([pizza_done, post_init], dispatch_uid='pizza_done')
def receiver_pizza_done(sender, **kwargs):
    print('pizza donen!')
    print(kwargs)
```



## 参考

> https://docs.djangoproject.com/en/2.0/ref/signals/