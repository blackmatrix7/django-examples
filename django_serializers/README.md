# Django Serialization

Django 序列化model的例子。

部分例子例子来自Django官方手册，对序列化部分进行实践和记录。

## 准备

### 环境

python 3.5.2

djang 2.0.5

sqlite3

### 创建项目

django-admin startproject proj

cd proj

python manange.py startapp app

## 开始

### 一些准备

#### 创建model

一个简单的一对多表结构

app/models.py

```python
from django.db import models

class Person(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    birthdate = models.DateField()

    def natural_key(self):
        return [self.first_name, self.last_name]

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
```

#### 写入测试数据

```sql
INSERT INTO "app_person"("id", "first_name", "last_name", "birthdate") VALUES ('1', 'Tom', 'Clancy', '1947/04/12');
INSERT INTO "app_book"("id", "name", "author_id") VALUES (1, 'Rainbow Six', 1);
```

#### 创建视图

用来获取表数据

```python
import json
from .models import Book
from django.http import JsonResponse
from django.core.serializers import serialize

# Create your views here.
def get_books(request):
    book = Book.objects.all()
    json_str = serialize('json', book, use_natural_foreign_keys=True)
    return JsonResponse({'books': json.loads(json_str)})
```

