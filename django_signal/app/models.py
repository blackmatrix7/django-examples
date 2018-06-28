from django.db import models

# Create your models here.


class Pizza(models.Model):

    toppings = models.CharField('配料', max_length=128)
    size = models.IntegerField('尺寸')
