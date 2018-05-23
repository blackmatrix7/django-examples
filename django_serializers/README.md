# Django Serialization

Django 序列化框架提供了一套将Django model转换称json、xml或yaml的方法。

#### 一些准备

创建下面两个Model

```python
from django.db import models

class Person(models.Model):
    
    class Meta:
        unique_together = (('first_name', 'last_name'),)
        
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField()

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
```

并插入一些测试数据

```sql
INSERT INTO "app_person"("id", "first_name", "last_name", "birthdate") VALUES ('1', 'Tom', 'Clancy', '1947/04/12');
INSERT INTO "app_book"("id", "name", "author_id") VALUES (1, 'Rainbow Six', 1);
```

#### 简单的序列化

直接使用serializers.serialize对queryset进行序列化。

```python
book = Book.objects.all()
json_str = serialize('json', Book.objects.all())
```

得到序列化之后的json

```json
[
    {
        "model":"app.book",
        "fields":{
            "author":1,
            "name":"Rainbow Six"
        },
        "pk":1
    }
]
```

#### Natural keys

仔细看上面的json，还有些需要完善的地方。

Book表中的author为外键，序列化完成后，只显示外键的值，而不是对象（ "author":1）。将序列化后的数据提供给前端时，返回author等于1的意义不大，前端更需要的应该是直接返回作者的姓名。

这个时候就需要使用natural keys。



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

### 一些简单的准备

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

#### 序列化对象

现在，我们创建一个视图，用来返回book表的数据。

```python
import json
from .models import Book
from django.http import JsonResponse
from django.core.serializers import serialize

# Create your views here.
def get_books(request):
    book = Book.objects.all()
    json_str = serialize('json', book)
    return JsonResponse({'books': json.loads(json_str)})
```

这里使用django的serialize方法，用于将model对象序列化成json。

serialize相关的可以参考Django官方手册

https://docs.djangoproject.com/en/2.0/topics/serialization/

#### 注册Url

proj/urls.py

```python
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', views.get_books),
]
```

