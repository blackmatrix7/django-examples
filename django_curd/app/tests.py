from datetime import datetime
from django.db.models import F
from django.test import TestCase
from django.db import transaction
from django.core.exceptions import *
from .models import Customer, Product, Tag


# Create your tests here.
class CURDTestCase(TestCase):

    def setUp(self):
        # 基础数据
        with transaction.atomic():
            default_update_time = datetime(year=2018, month=5, day=1, hour=8, minute=10, second=30)
            Customer.objects.bulk_create([Customer(name=name, age=age)
                                          for (name, age) in
                                          (('张三', 21), ('李四', 72), ('王五', 21), ('刘六', 13))])
            Product.objects.bulk_create([Product(id=id_, name=name, price=price,
                                                 member_price=member_price, update_time=update_time)
                                         for (id_, name, price, member_price, update_time) in
                                         ((1, '手机', 3999, 3700, default_update_time),
                                          (2, '电脑', 7999, 8000, default_update_time),
                                          (3, '耳机', 399, 299, default_update_time),
                                          (4, '矿泉水', 2, 2, default_update_time),
                                          (5, '饼干', 2, 2, default_update_time))])
            Tag.objects.create(name='食品')
            Tag.objects.create(name='电子产品')

    def test_get(self):
        """
        查询
        :return:
        """
        # 获取唯一的对象
        customer = Customer.objects.get(id=1)
        self.assertEqual(customer.name, '张三')
        # 如果对象不唯一则抛出MultipleObjectsReturned异常
        with self.assertRaises(MultipleObjectsReturned):
            Customer.objects.get(age=21)
        # 查询不到对象抛出ObjectDoesNotExist
        with self.assertRaises(ObjectDoesNotExist):
            Customer.objects.get(id=999)

    def test_get_or_create(self):
        """
        新增或创建
        :return:
        """
        # 查询或创建对象，返回一个元组，第一个元素为查询或创建的对象，第二个为是否新建的对象
        customer, create = Customer.objects.get_or_create(name='郭七', age=56)
        self.assertEqual(customer.name, '郭七')

    def test_order_by(self):
        """
        排序
        :return:
        """
        # 升序
        customers = Customer.objects.order_by('age').first()
        self.assertEqual(customers.name, '刘六')
        # 降序
        customers = Customer.objects.order_by('-age').first()
        self.assertEqual(customers.name, '李四')

    def test_filter_exculde(self):
        """
        filter and exculde
        :return:
        """
        # 查询age为21，而name不为张三的
        customer = Customer.objects.filter(age=21).exclude(name='张三').order_by('id').first()
        self.assertEqual(customer.name, '王五')

    def test_return_list(self):
        # 返回QuertSet，每个元素都是tuple
        customers = Customer.objects.values_list('name').all()
        for customer in customers:
            self.assertIsInstance(customer, tuple)
        # flat=True时，返回QuertSet，所有的数据组成list
        customers = Customer.objects.values_list('name', flat=True).all()
        for customer in customers:
            self.assertIsInstance(customer, str)
        # 查询单条数据
        customer = Customer.objects.values_list('name').first()
        self.assertIsInstance(customer, tuple)

    def test_f_object(self):
        # F对象，使用查询条件中字段的值，参与比较
        # 查询会员价大于零售价的商品，可能是大数据杀熟
        product_list = Product.objects.filter(member_price__gte=F('price')).all()
        assert product_list[0].name
        self.assertEqual(product_list[0].name, '电脑')
        # 电脑涨价
        Product.objects.filter(name='电脑').update(price=F('price')+100)
        # 需要重新取值，否则内存中的product价格是旧的
        product = Product.objects.get(name='电脑')
        self.assertEqual(product.price, 8099)

    def test_update_or_create(self):
        """
        update_or_create 返回tuple
        :return:
        """
        # update
        # update_or_create接口kw类型的参数，前面的参数为查询条件，defaults参数接受一个dict，为需要修改的数据
        # 下面的语句，意思是查询名为"耳机"的商品，如果存在的话，将member_price改为388
        product = Product.objects.update_or_create(name='耳机', defaults={'member_price': 388})[0]
        self.assertEqual(product.member_price, 388)
        self.assertEqual(product.id, 3)  # 耳机id为3，id不变，所以是update
        # create
        product = Product.objects.update_or_create(name='电视', defaults={'price': 3999, 'member_price': 2999})[0]
        self.assertEqual(product.id, 6)  # create, id 应该为6

    def test_bulk_create(self):
        """
        批量新增
        对比于for循环中save的方式，bulk_create的执行效率更高，因为前者每save一次执行一次insert语句
        :return:
        """
        product_list = [Product(name=name, price=price, member_price=member_price)
                        for (name, price, member_price) in (('蓝色水笔', 4, 4), ('黑色水笔', 5, 3), ('红色水笔', 5, 2))]
        Product.objects.bulk_create(product_list, 100)
        self.assertEqual(Product.objects.filter(name__endswith='水笔').count(), 3)

    def test_auto_now(self):
        """
        auto_now只对save()方法有效，其他的如query_set.update()是无效的
        :return:
        """
        # 通过save方法是有效的
        computer = Product.objects.get(name='电脑')
        computer_update_time = computer.update_time
        computer.price = 9999
        computer.save()
        # 修改前后的update_time不同，说明update_time已更新
        self.assertNotEqual(computer.update_time, computer_update_time)
        # 通过update方法就无效了
        phone = Product.objects.get(name='手机')
        phone_update_time = phone.update_time
        Product.objects.filter(name='手机').update(price=6000)
        phone = Product.objects.get(name='手机')
        # 修改前后的update_time相同，说明update_time并没有更新
        self.assertEqual(phone.update_time, phone_update_time)
        # update时的做法，手动更新update_time
        Product.objects.filter(name='手机').update(price=6000, update_time=datetime.now())

    def test_many_to_many(self):
        """
        测试多对多，没有自己指定关系表
        :return:
        """
        pass
        # 新增标签与商品的关系
        # product = Product.objects.get(name='手机')
        # product

    def tearDown(self):
        pass
