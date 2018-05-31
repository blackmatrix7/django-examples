from django.db import models

# Create your models here.


class Tag(models.Model):

    name = models.CharField('标签', max_length=24)
    products = models.ManyToManyField('Product')


class Product(models.Model):

    name = models.CharField('商品名称', max_length=24)
    price = models.DecimalField('价格', max_digits=10, decimal_places=6)


class Customer(models.Model):

    name = models.CharField('姓名', max_length=24)
    age = models.IntegerField('年龄')
    products = models.ManyToManyField(Product, through='Shopping', through_fields=('customer', 'product'))


class Shopping(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    count = models.IntegerField('总数')


