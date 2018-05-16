from django.db import models


# Create your models here.
class Boss(models.Model):

    class Meta:
        db_table = 'Boss'

    name = models.CharField('老板姓名', max_length=12)
    age = models.IntegerField('老板年龄')
