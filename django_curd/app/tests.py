import decimal
from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from django.db import transaction
from django.core.exceptions import *
from django.db.models import DecimalField, F, Q, Sum, Max, Min, Avg, Count
from .models import Customer, Product, Tag


# Create your tests here.
class CURDTestCase(TestCase):

    def setUp(self):
        # 统一精度
        decimal.getcontext().prec = 28
        # 基础数据
        with transaction.atomic():
            self.default_update_time = datetime(year=2018, month=5, day=1, hour=8, minute=10, second=30)

            self.tag_list = ((1, '电子产品',),
                             (2, '食品',))

            self.product_list = ((1, '手机', 3999, 3700, self.default_update_time),
                                 (2, '电脑', 7999, 8000, self.default_update_time),
                                 (3, '耳机', 399, 299, self.default_update_time),
                                 (4, '矿泉水', 1, 1, self.default_update_time),
                                 (5, '饼干', 2, 2, self.default_update_time),
                                 (6, '矿泉水', 2, 2, self.default_update_time))

            self.customer_list = ((1, '王一', 21, '15689776542'),
                                  (2, '周二', 72, '13034451353'),
                                  (3, '张三', 21, '13248642709'),
                                  (4, '李四', 13, '13252034306'))

            # 商品标签数据
            digital, food, *_ = Tag.objects.bulk_create(Tag(id=id_, name=name) for (id_, name, ) in self.tag_list)
            # 商品数据
            products = Product.objects.bulk_create(Product(id=id_, name=name, price=price, member_price=member_price,
                                                           update_time=update_time)
                                                   for (id_, name, price, member_price, update_time) in self.product_list)
            # 客户数据
            Customer.objects.bulk_create(Customer(id=id_, name=name, age=age, phone=phone)
                                         for (id_, name, age, phone) in self.customer_list)
            # 更新商品标签
            for product in products:
                if product.name in ('手机', '电脑', '耳机'):
                    product.tags.add(digital)
                else:
                    product.tags.add(food)

    def test_get(self):
        """
        查询
        :return:
        """
        # 获取唯一的对象
        customer = Customer.objects.get(id=1)
        self.assertEqual(customer.name, '王一')
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
        customer, created = Customer.objects.get_or_create(name='郭七', age=56)
        self.assertEqual(customer.name, '郭七')

    def test_bulk(self):
        """
        根据主键或不允许重复的字段快速查询数据
        :return:
        """
        # in_bulk 接受id_list和field_name两个参数
        # field_name 默认参数为pk，即使用主键进行查询
        # 下面的查询语句中，查询的是主键id为1、2、3、4的数据
        product_list = Product.objects.in_bulk([1, 2, 3, 4])
        # 检验通过
        for index, (*_, product) in enumerate(product_list.items(), 1):
            self.assertEqual(index, product.id)
        # field_name传入不重复的字段，也可以根据field_name查询
        phone_list = [(phone for (*_, phone) in self.customer_list)]
        customer_list = Customer.objects.in_bulk(phone_list, field_name='phone')
        for index, customer in enumerate(customer_list):
            self.assertEqual(phone_list[index], customer.phone)

    def test_bulk_create(self):
        """
        批量新增
        对比于for循环中save的方式，bulk_create的执行效率更高，因为前者每save一次执行一次insert语句
        :return:
        """
        product_list = [Product(name=name, price=price, member_price=member_price)
                        for (name, price, member_price) in (('蓝色水笔', 4, 4), ('黑色水笔', 5, 3), ('红色水笔', 5, 2))]
        # bulk_create 返回list，list内是创建的model
        create_list = Product.objects.bulk_create(product_list, 100)
        self.assertIsNotNone(create_list)
        self.assertEqual(Product.objects.filter(name__endswith='水笔').count(), 3)

    def test_update(self):
        """
        对queryset查询出来的数据进行update
        update是数据库级别的操作， 不会触发save()
        :return:
        """
        # 例如，对售价大于10元的商品，涨价1元
        affected = Product.objects.filter(price__gte=10).update(price=F('price')+1)
        self.assertTrue(affected > 0)
        # 初始化数据中，id为1的商品，初始的金额
        old_price = [product for product in self.product_list if product[0] == 1][0][2]
        self.assertEqual(Decimal(old_price + 1), Product.objects.get(id=1).price)

        # 更新某个数据时，应该使用update()，而不是将model查询出来，修改后再save()
        # 前者可以避免竞态条件，后者有可能在取出数据，至重新save()期间，数据被修改
        # 避免下面的操作，除非save()方法有一些自定义逻辑，比如会员价会自动根据零售价打折
        # product = Product.objects.get(id=1)
        # product.price += 10
        # product.save()

        # 对Queryset进行切片时，无法使用update
        with self.assertRaises(AssertionError):
            # AssertionError: Cannot update a query once a slice has been taken.
            Product.objects.filter(price__gte=10)[1: 2].update(price=F('price')+1)

        # update只能更新model自身的字段，而不能更新关联的model的字段
        # 例如 Tag model关联了Product Model，通过 Tag model去更新Product的字段是不可行的
        # 假设需求是食品通通免费啦
        with self.assertRaises(FieldDoesNotExist):
            # django.core.exceptions.FieldDoesNotExist: Tag has no field named 'product__price'
            Tag.objects.filter(name='食品').update(product__price=0)
        # 正确的做法
        Product.objects.filter(tags__name='食品').update(price=0)
        phone = Product.objects.filter(name='手机').first()
        self.assertTrue(phone.price > 0)
        cookie = Product.objects.filter(tags__name='食品', name='饼干').first()
        self.assertTrue(cookie.price == 0)

    def test_delete(self):
        """
        对queryset的查询结果进行delete
        :return:
        """
        # TODO 写累了，下次补充，加个todo免得忘了
        pass

    def test_update_or_create(self):
        """
        update_or_create 返回tuple
        :return:
        """
        # update 更新或创建对象，返回一个元组，第一个元素为查询或创建的对象，第二个为是否新建的对象
        # update_or_create接口kw类型的参数，前面的参数为查询条件，defaults参数接受一个dict，为需要修改的数据
        # 下面的语句，意思是查询名为"耳机"的商品，如果存在的话，将member_price改为388
        product, created = Product.objects.update_or_create(name='耳机', defaults={'member_price': 388})
        self.assertFalse(created)  # 没有创建新的数据，所以created为False
        self.assertEqual(product.member_price, 388)
        self.assertEqual(product.id, 3)  # 耳机id为3，id不变，所以是update
        # create
        product, created = Product.objects.update_or_create(name='电视', defaults={'price': 3999, 'member_price': 2999})
        self.assertTrue(created)  # 创建新的数据，所以created为True
        self.assertEqual(product.id, len(self.product_list) + 1)  # create, id 应该自增

    def test_order_by(self):
        """
        排序
        :return:
        """
        # 升序
        customers = Customer.objects.order_by('age').first()
        self.assertEqual(customers.name, '李四')
        # 降序
        customers = Customer.objects.order_by('-age').first()
        self.assertEqual(customers.name, '周二')

    def test_filter_exculde(self):
        """
        filter and exculde
        :return:
        """
        # 查询age为21，而name不为张三的
        customer = Customer.objects.filter(age=21).exclude(name='张三').order_by('id').first()
        self.assertEqual(customer.name, '王一')

    def test_values(self):
        """
        以dict返回数据查询结果
        :return:
        """
        # values函数可以指定字段，如果不指定，则是包含查询结果的所有字段
        product_list = Product.objects.values('id', 'name', 'price')
        for product in product_list:
            self.assertTrue(isinstance(product, dict))
            self.assertIn('id', product)
            self.assertIn('name', product)
            self.assertIn('price', product)
            self.assertNotIn('update_time', product)
        # 同only一起使用时，values会覆盖only指定的字段
        product_list = Product.objects.only('id', 'name', 'price').values('member_price')
        for product in product_list:
            # 查询出的dict只会有 member_price
            self.assertTrue(isinstance(product, dict))
            self.assertNotIn('id', product)
            self.assertNotIn('name', product)
            self.assertNotIn('price', product)
            self.assertIn('member_price', product)
        # values 和 values_list 必须在 only 之后
        with self.assertRaises(TypeError):
            # TypeError: Cannot call only() after .values() or .values_list()
            Product.objects.values('member_price').only('id', 'name', 'price')
        # 还可以为value指定key
        product_list = Product.objects.values(product_id=F('id'))
        for product in product_list:
            # 查询出的dict只会有 member_price
            self.assertTrue(isinstance(product, dict))
            # 此时没有 id，只有 product_id 了
            self.assertIn('product_id', product)

    def test_values_list(self):
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

    def text_exists(self):
        """
        检查数据是否存在
        :return:
        """
        """
        exists 函数用于检查queryset的数据是否存在
        queryset是惰性查询的，当django返回queryset时，其实并没有在数据库中进行任何操作
        只有当访问访问queryset时，才会将queryset查询的内容加载到内存中
        如使用if语句，或对queryset进行迭代时，都会触发queryset进行查询
        在大数据量的查询中，一次性将这些数据加载到内存中，可能导致内存溢出
        所以当只是想判断数据是否存在时，可以使用exists函数
        """
        # 假设查询李四是否在成年的客户中
        # 第一种方法
        lisi = Customer.objects.get(name='李四')
        cutomer_list = Customer.objects.filter(age__gte=18)
        # 在assertNotIn时，需要执行cutomer_list的queryset，将所有的对象加载到内存中，再进行判断
        self.assertNotIn(lisi, cutomer_list)
        # 第二种方法
        self.assertFalse(Customer.objects.filter(age__gte=18).exists(name='李四'))
        self.assertTrue(Customer.objects.filter(age__gte=18).exists(name='王一'))
        # 第二种方法性能好于第一种

    def test_defer(self):
        """
        defer
        :return:
        """
        prodcut_list = Product.objects.defer('update_time').all()
        # 查询语句中没有查询 update_time 字段
        self.assertNotIn('update_time', str(prodcut_list.query))
        # defer仍会返回QuerySet对象，defer里字段的值，会延迟查询，直到主动访问这个字段
        # 就是说 prodcut_list 这个 QuerySet，对于defer中的update_time字段，是延迟查询的
        # 但是，如果主动去访问这个字段，仍然会查询出update_time的值
        for product in prodcut_list:
            # 主动去访问update_time字段的值，仍会查询
            self.assertIsNotNone(product.update_time)
        # 多次调用defer的时，每次调用defer时排除的字段，都会生效
        prodcut_list = Product.objects.defer('update_time').defer('member_price').all()
        # 查询语句中没有查询 update_time 字段
        self.assertNotIn('update_time', str(prodcut_list.query))
        # 查询语句中没有查询 member_price 字段
        self.assertNotIn('member_price', str(prodcut_list.query))
        # 不能defer主键，或者说defer也没用
        prodcut_list = Product.objects.defer('id').all()
        # 查询语句中存在 id 字段
        self.assertIn('id', str(prodcut_list.query))
        # 如果不希望每次都使用defer，可以创建同名的model，只要将managed设置为False即可
        from django.db import models

        class ProductNoUpdateTime(models.Model):

            name = models.CharField('商品名称', max_length=24)
            price = models.DecimalField('零售价', max_digits=10, decimal_places=6)
            member_price = models.DecimalField('会员价', max_digits=10, decimal_places=6, null=True, blank=True)

            class Meta:
                managed = False
                db_table = 'product'
        # 两个查询语句是等同的
        prodcut_no_updatetime_list = ProductNoUpdateTime.objects.all()
        prodcut_list = Product.objects.defer('update_time').all()
        self.assertEqual(str(prodcut_list.query), str(prodcut_no_updatetime_list.query))

    def test_only(self):
        """
        only和defer的相似
        :return:
        """
        # only 只查询某些字段
        prodcut_list = Product.objects.only('name').all()
        # 只查询name时，不会查询update_time
        self.assertNotIn('update_time', str(prodcut_list.query))
        # 即使只查询name，主键也是会强制查询的
        self.assertIn('id', str(prodcut_list.query))
        # 多次调用only，只有最后一次调用有效
        prodcut_list = Product.objects.only('name').only('price').all()
        self.assertIn('price', str(prodcut_list.query))
        self.assertNotIn('name', str(prodcut_list.query))
        # only和defer同时调用
        # only在前，defer在后，查询的字段为二者的差集
        prodcut_list = Product.objects.only('name', 'price').defer('price').all()
        self.assertIn('name', str(prodcut_list.query))
        self.assertNotIn('price', str(prodcut_list.query))
        # 差集查询的字段为空时，则查询全部字段
        prodcut_list = Product.objects.only('price').defer('name', 'price').all()
        self.assertIn('name', str(prodcut_list.query))
        self.assertIn('price', str(prodcut_list.query))
        # defer在前，only在后，查询的字段为二者的差集
        prodcut_list = Product.objects.defer('price').only('name', 'price').all()
        self.assertIn('name', str(prodcut_list.query))
        self.assertNotIn('price', str(prodcut_list.query))
        # 差集查询的字段为空时，则查询全部字段
        prodcut_list = Product.objects.defer('name', 'price').only('price').all()
        self.assertIn('name', str(prodcut_list.query))
        self.assertIn('price', str(prodcut_list.query))

    def test_aggregate(self):
        """
        Django 聚合函数
        :return:
        """
        # output_field 可以设置输出的字段类型
        # Sum
        data = Product.objects.aggregate(price=Sum(F('price'), output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(sum((item[2] for item in self.product_list))))
        # Max
        data = Product.objects.aggregate(price=Max(F('price'), output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(max((item[2] for item in self.product_list))))
        # Min
        data = Product.objects.aggregate(price=Min(F('price'), output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(min((item[2] for item in self.product_list))))
        # Avg
        data = Product.objects.aggregate(price=Avg(F('price'), output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(sum((item[2] for item in self.product_list)) / len(self.product_list)))
        # Count
        # Count还有个参数为distinct，默认为False，当为True时，只统计不重复的数据
        data = Product.objects.aggregate(count=Count(F('price')))
        self.assertEqual(data['count'], len(self.product_list))

    def test_select_for_update(self):
        """
        SQLite下无效， 需要mysql
        :return:
        """
        # TODO 待补充完成
        pass

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
