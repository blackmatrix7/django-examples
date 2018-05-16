from django.db import models


# Create your models here.
class Client(models.Model):

    class Meta:
        db_table = 'Client'

    name = models.CharField('乘客姓名', max_length=12)
    age = models.IntegerField('乘客年龄')
