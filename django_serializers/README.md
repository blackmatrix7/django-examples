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

这个时候就需要使用natural keys，修改原先的Person Model，增加natural_key方法，返回first_name与last_name。

app/models.py

```python
class Person(models.Model):

    class Meta:
        unique_together = (('first_name', 'last_name'),)

    birthdate = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def natural_key(self):
        return [self.first_name, self.last_name]
```

修改序列化时的方法，增加参数use_natural_foreign_keys=True

app/views.py

```python
json_str = serialize('json', Book.objects.all(), use_natural_foreign_keys=True)
```

重新进行序列化后，可以看到author不为1，而是返回first_name和last_name

```json
{
    "books":[
        {
            "pk":1,
            "model":"app.book",
            "fields":{
                "author":[
                    "Tom",
                    "Clancy"
                ],
                "name":"Rainbow Six"
            }
        }
    ]
}
```



## 准备

### 环境

python 3.5.2

djang 2.0.5

sqlite3

### 需要的包

Django 2.0.5

### 运行

python manage.py runserver

访问 http://127.0.0.1:8000/books/