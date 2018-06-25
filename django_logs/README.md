# Django Logs

Django 日志相关的配置。

## 准备

### 环境

python 3.5.2

djang 2.0.5

### 创建项目

使用命令快速新建django项目，示例的项目名为proj。

## 开始

### 修改配置文件

日志部分配置，参考Django官方手册

https://docs.djangoproject.com/en/2.0/topics/logging/#examples

LOGGING属性实际上是一个dictConfig

关于dictConfig的配置，参考Python官方手册

https://docs.python.org/3/library/logging.config.html#logging-config-dictschema

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        # 输出日志的控制台
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # 输出日志到文件，按日期滚动
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            # TimedRotatingFileHandler的参数
            # 参照https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
            # 目前设定每天一个日志文件
            'filename': 'logs/manage.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 100,
            'formatter': 'verbose'
        },
        # 发送邮件，目前腾讯云、阿里云的服务器对外发送邮件都有限制，暂时不使用
        'email': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        # 不同的logger
        'django': {
            'handlers': ['console', 'file', 'email'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 创建logs目录

```shell
cd django_logs/
mkdir logs
```

### 新增django_logs/logger.py

注意保证logger.py在启动时会被加载，以运行logging模块从dictConfig读取配置的代码。

```python

import logging.config
from django.conf import settings

logger = logging.getLogger('django')
# logging模块从dictConfig中读取配置，这样logging.info('xxx')也可以直接输出日志
logging.config.dictConfig(settings.LOGGING)
```

## 验证

### 创建app

```
python manage.py startapp app
```

### 编写视图函数

编写一个视图函数，用于往日志文件写入日志

django_logs/app/views.py

```python
from logger import logger
from django.shortcuts import HttpResponse

def test_logger(request):
    logger.info('test log')
    return HttpResponse('test log')
```

### 配置Url

django_logs/proj/urls.py

```python
from app import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test_log/', views.test_logger),
]
```

### 调用

访问 [http://127.0.0.1:8000/test_log/](http://127.0.0.1:8000/test_log/) ，在logs/manage.log中成功写入

```
[2018-05-18 08:35:44,317] [INFO] test log
[2018-05-18 08:35:44,318] [INFO] "GET /test_log/ HTTP/1.1" 200 8
```

最后，调整系统时间，可以看到日志文件会根据系统时间滚动。