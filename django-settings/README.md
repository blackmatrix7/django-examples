# django settings

django 配置文件使用记录

### 初始

使用命令快速新建django项目，示例的项目名为proj。

### 支持本地的配置文件

#### 特性

1. 支持django自带的--setttings参数
2. 支持自定义的cfg参数
3. 支持本地配置文件
4. 支持gunicorn

#### 配置说明

复制cmdline到项目中，路径自定，示例中设置的是toolkit.cmdline。

修改项目根目录的manage.py，需要修改的地方已经在注释中说明

```python
#!/usr/bin/env python
import os
from toolkit.cmdline import cmdline

if __name__ == "__main__":
    # 将 "proj.settings" 改为cmdline.settings，注意没有引号
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", cmdline.settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # 修改 sys.argv 为 cmdline.command
    execute_from_command_line(cmdline.command)
```

#### 创建配置文件

在项目根目录下，创建settings和local_settings两个包，用于存放配置文件。同时修改.gitignore，避免将local_settings目录上传的git服务器。

在settings或local_settings的目录中，可以创建数个py文件，每个py文件都可以作为独立的配置文件，py文件名即配置文件名。

#### 配置文件的继承

如果需要继承其他配置文件，可以在配置文件的顶部，通过`from xxx import xxx`加载其他配置文件中项目。

例如`from .common import *`，代表从同级目录的common中继承配置文件项目。

#### 配置文件优先顺序

如果项目根目录中不存在local_settings，则直接使用settings的配置。

如果项目根目录下同时存在local_settings和settings，则优先使用local_settings配置文件，只有当local_settings不存在时，才会使用settings的配置。

例如：

项目同时存在 settings/default.py和local_settings/default.py，加载时会优先使用local_settings/default.py。

#### 启动项目

使用命令 python manage.py -cfg=default runserver启动项目。

default为settings或local_settings目录下的py文件，default即对应default.py。

如果使用django自带的—settings参数启动项目，则本地配置文件local_settings不会生效，实际生效的是—settings参数指定的py文件，这点和django原来是完全一样的。

### 通过配置文件设定HOST和PORT

默认情况下，django需要在启动的时候指定host和port。但每次使用都输入这两个参数还是比较繁琐的。

可以通过修改manage.py，实现通过配置文件设定host和port，而不需要每次启动时手动指定。

修改的地方见注释。

```python
#!/usr/bin/env python
import os
# 载入settings
from django.conf import settings
from toolkit.cmdline import cmdline

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", cmdline.settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    from django.core.management.commands.runserver import Command
    # 修改默认地址
    Command.default_addr = settings.HOST
    # 修改默认端口号
    Command.default_port = settings.PORT
    execute_from_command_line(cmdline.command)
```

