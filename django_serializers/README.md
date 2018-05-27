# Django Serialization

Django 序列化框架提供了一套将Django model转换称json、xml或yaml的方法。

### 一些准备

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

### 序列化

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
[
    {
        "model": "app.book",
        "fields": {
            "name": "Rainbow Six",
            "author": [
                "Tom",
                "Clancy"
            ]
        },
        "pk": 1
    }
]
```

### 反序列化

#### 简单的反序列化

反序列化的操作也是十分简单，使用serializers模块的deserialize方法即可。

```python
json_str = '[{"model":"app.book","fields":{"name":"RainbowSix","author": 1}}, {"model":"app.book","fields":{"name":"NightMoves","author": 1}}]'

serializers.deserialize('json', json_str)
```

#### 保存到数据库

迭代反序列化后的对象，迭代的每个元素是DeserializedObject，而不是Django的model。

调用DeserializedObject实例的save()方法，将其保存到数据库。

```python
# json_str 同上个例子
for deserialized_object in serializers.deserialize('json', json_str):
	deserialized_object.save()
```

需要注意的是，保存到数据库时，最好检查一下数据的完整性，数据不完整时，保存到数据库有可能失败。

比如下面的例子，name为null，而数据库不允许为null，就会出现异常：django.db.utils.IntegrityError: NOT NULL constraint failed: app_book.name。

```Python
json_str = '[{"model":"app.book","fields":{"name":null,"author":["Tom","Clancy"]}},{"model":"app.book","fields":{"name":null,"author":["Tom","Clancy"]}}]'

for deserialized_object in serializers.deserialize('json', json_str):
    deserialized_object.save()
```

##### PK

反序列化的Json对象中，没有pk(主键)时会进行新增，如上文中的json_str，会直接新增对象到数据库。

如果存在则会对数据进行更新，如下面的json中，将Rainbow Six改成Rainbow Six2，save后，数据库中的数据也会随之改变。

```python
json_str = '[{"fields":{"author":1,"name":"Rainbow Six2"},"pk":1,"model":"app.book"},{"fields":{"author":1,"name":"Night Moves"},"pk":2,"model":"app.book"}]'

for deserialized_object in serializers.deserialize('json', json_str):
        deserialized_object.save()
```

#### get_by_natural_key

对于使用了Natural keys的数据，反序列化时，可以使用get_by_natural_key，获取natural_key的唯一对象，并参与反序列化。

还是以之前的Person为例，定义一个Manager，并将其实例赋值给Person的objects属性。

app/models.py

```python
class PersonManager(models.Manager):

    def get_by_natural_key(self, first_name, last_name):
        return self.get(first_name=first_name, last_name=last_name)
    
class Person(models.Model):

    objects = PersonManager()

    class Meta:
        unique_together = (('first_name', 'last_name'),)

    birthdate = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def natural_key(self):
        return [self.first_name, self.last_name]
```

还是进行反序列化，这个时候author为["Tom","Clancy"]，而不再是1。反序列化时，会调用PersonManager的get_by_natural_key方法，获取Person Object，并作为外键关联。

```python
json_str = '[{"model":"app.book","fields":{"name":"RainbowSix","author":["Tom","Clancy"]}}, {"model":"app.book","fields":{"name":"NightMoves","author":["Tom","Clancy"]}}]'

serializers.deserialize('json', json_str)
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