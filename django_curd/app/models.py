from django.db import models

# Create your models here.


class BaseModel(models.Model):

    class Meta:
        abstract = True

    is_deleted = models.BooleanField('是否删除', default=False)


class SoftDelManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Tag(BaseModel):

    objects = SoftDelManager()

    class Meta:
        db_table = 'tag'

    name = models.CharField('标签', max_length=24)


class Supplier(BaseModel):

    objects = SoftDelManager()

    class Meta:
        db_table = 'supplier'

    name = models.CharField('供应商', max_length=120)
    address = models.CharField('地址', max_length=512)


class Product(BaseModel):

    objects = SoftDelManager()

    class Meta:
        db_table = 'product'

    name = models.CharField('商品名称', max_length=24)
    price = models.DecimalField('零售价', max_digits=40, decimal_places=28)
    member_price = models.DecimalField('会员价', max_digits=40, decimal_places=28, null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True, blank=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT, verbose_name='供应商', null=True, blank=True)
    tags = models.ManyToManyField('Tag')


class Customer(BaseModel):

    objects = SoftDelManager()

    class Meta:
        db_table = 'customer'

    name = models.CharField('姓名', max_length=24)
    age = models.IntegerField('年龄')
    products = models.ManyToManyField(Product, through='Shopping', through_fields=('customer', 'product'))
    phone = models.CharField('手机', max_length=11, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Shopping(BaseModel):

    class Meta:
        db_table = 'shopping'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    count = models.IntegerField('总数')



