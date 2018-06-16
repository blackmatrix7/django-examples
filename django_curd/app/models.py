from django.db import models

# Create your models here.


class Tag(models.Model):

    class Meta:
        db_table = 'tag'

    name = models.CharField('标签', max_length=24)
    products = models.ManyToManyField('Product')


class Product(models.Model):

    class Meta:
        db_table = 'product'

    name = models.CharField('商品名称', max_length=24)
    price = models.DecimalField('零售价', max_digits=10, decimal_places=6)
    member_price = models.DecimalField('会员价', max_digits=10, decimal_places=6, null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True, blank=True)


class Customer(models.Model):

    class Meta:
        db_table = 'customer'

    name = models.CharField('姓名', max_length=24)
    age = models.IntegerField('年龄')
    products = models.ManyToManyField(Product, through='Shopping', through_fields=('customer', 'product'))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Shopping(models.Model):

    class Meta:
        db_table = 'shopping'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    count = models.IntegerField('总数')



