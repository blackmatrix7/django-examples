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

```python
import logging

logger = logging.getLogger('django')
```

