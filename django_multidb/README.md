# Django MultiDB

Django 多数据库配置，为每个App配置独立的数据库。

## 准备

### 环境

python 3.5.2

djang 2.0.5

### 创建项目

使用命令快速新建django项目，示例的项目名为proj。

## 开始

### 创建DataBase Router

在proj目录下创建database_router.py

```python
from django.conf import settings

DATABASE_MAPPING = settings.DATABASE_APPS_MAPPING


class DatabaseAppsRouter:

    @staticmethod
    def db_for_read(model, **hints):
        """"Point all read operations to the specific database."""
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    @staticmethod
    def db_for_write(model, **hints):
        """Point all write operations to the specific database."""
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        db_obj1 = DATABASE_MAPPING.get(obj1._meta.app_label)
        db_obj2 = DATABASE_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    # for Django 1.4 - Django 1.6
    @staticmethod
    def allow_syncdb(db, model):
        """Make sure that apps only appear in the related database."""

        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(model._meta.app_label) == db
        elif model._meta.app_label in DATABASE_MAPPING:
            return False
        return None

    # Django 1.7 - Django 1.11
    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(app_label) == db
        elif app_label in DATABASE_MAPPING:
            return False
        return None
```

### 修改配置文件

增加多组数据库配置，这里都使用sqlite。

最好保留default，便于django admin使用。

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'proj.sqlite3'),
    },
    'client': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'client.sqlite3'),
    },
    'driver': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'driver.sqlite3'),
    },
    'boss': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'boss.sqlite3'),
    }
}
```

增加django router的配置，并且每个app指定一个数据库配置

```python
DATABASE_ROUTERS = ['proj.database_router.DatabaseAppsRouter']

DATABASE_APPS_MAPPING = {
    'boss': 'boss',
    'client': 'client',
    'driver': 'driver'
}
```

### 生成数据库迁移脚本

`python manage.py makemigrations`

### 迁移数据库

这里需要对每个数据库单独进行迁移，在migrate后面增加参数—database，为其单独进行迁移。

多个数据库的情况下，需要针对每个数据单独运行迁移脚本，demo中存在三个数据：boss、client、driver，所以需要单独迁移三次。

`python manage.py migrate --database=boss`

`python manage.py migrate --database=client`

`python manage.py migrate --database=driver`

## 验证

### 使用views验证

增加views，访问时添加数据，用来验证配置是否成功。

boss/views.py

```python
from .models import Boss
from django.shortcuts import HttpResponse


# Create your views here.
def add_boss(request):
    Boss(name=request.GET['name'], age=request.GET['age']).save()
    return HttpResponse('success')
```

proj/urls.py

```python
from django.urls import path
from boss.views import add_boss
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_boss/', add_boss),
]
```

访问： http://127.0.0.1:8000/add_boss/?name=jack&age=47 返回success。

查询boss.sqlit3里的boss表，确认数据添加成功。

其他的App同样添加类型的views，以进一步验证。

http://127.0.0.1:8000/add_driver/?name=Ace&age=43

http://127.0.0.1:8000/add_client/?name=Park&age=76

### 使用admin验证

boss/admin.py

```python
from django.contrib import admin
from .models import Boss

# Register your models here.
admin.site.register(Boss)
```

其他的app也进行类型的配置，最终在django admin中操作， 同样也可以确认不同的app存储在不同的数据库中，所以这样的配置对django admin也是同样有效的。