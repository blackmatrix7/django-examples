import decimal
from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from django.db import transaction
from django.core.exceptions import *
from django.db.models.deletion import ProtectedError
from django.db.models import DecimalField, F, Q, Sum, Max, Min, Avg, Count
from .models import BaseModel, SoftDelManager, Customer, Product, Tag, Supplier, Order


# Create your tests here.
class CURDTestCase(TestCase):

    def setUp(self):
        # 统一精度
        decimal.getcontext().prec = 28
        # 基础数据
        with transaction.atomic():
            self.default_update_time = datetime(year=2018, month=5, day=1, hour=8, minute=10, second=30)

            # 商品标签数据
            self.tag_list = ((1, '电子产品',),
                             (2, '食品',),
                             (3, '饮料'))
            digital, food, drink = Tag.objects.bulk_create(Tag(id=id_, name=name) for (id_, name, ) in self.tag_list)

            # 供应商
            self.supplier_list = ((1, '思想科技', '劳动路2333号'),
                                  (2, '鸭梨电子', '雷布斯路542号'),
                                  (3, '农妇食品', '长乐路1111号'),
                                  (4, '桶一食品', '无地址'))
            sixiang, yali, nongfu, tongyi = Supplier.objects.bulk_create(Supplier(id=id_, name=name, address=address)
                                                                         for (id_, name, address) in self.supplier_list)

            # 商品
            self.product_list = ((1, '手机', 3999, 3700, self.default_update_time, sixiang),
                                 (2, '电脑', 7999, 8000, self.default_update_time, yali),
                                 (3, '耳机', 399, 299, self.default_update_time, sixiang),
                                 (4, '矿泉水', 1, 1, self.default_update_time, nongfu),
                                 (5, '饼干', 2, 2, self.default_update_time, tongyi),
                                 (6, '矿泉水', 2, 2, self.default_update_time, tongyi))
            products = Product.objects.bulk_create(Product(id=id_, name=name, price=price, member_price=member_price,
                                                           update_time=update_time, supplier=supplier)
                                                   for (id_, name, price, member_price, update_time, supplier)
                                                   in self.product_list)

            # 顾客
            self.customer_list = ((1, '王一', 21, '15689776542'),
                                  (2, '周二', 72, '13034451353'),
                                  (3, '张三', 21, '13248642709'),
                                  (4, '李四', 13, '13252034306'),
                                  (5, 'Tom', 23, '13221042300'))
            wangyi, zhouer, zhangsan, lisi, tom = Customer.objects.bulk_create(Customer(id=id_, name=name, age=age, phone=phone)
                                                                               for (id_, name, age, phone) in self.customer_list)
            # 更新商品信息
            # 多对多的字段，需要先save
            digital.save()
            food.save()
            drink.save()
            for product in products:
                if product.name in ('手机', '电脑', '耳机'):
                    product.tags.add(digital)
                elif product.name in ('矿泉水',):
                    product.tags.add(food)
                    product.tags.add(drink)
                else:
                    product.tags.add(food)

            # 新增购物记录
            Order.objects.bulk_create([
                Order(customer=wangyi, product=products[0], count=2),
                Order(customer=wangyi, product=products[3], count=5),
                Order(customer=wangyi, product=products[4], count=10),
                Order(customer=zhouer, product=products[1], count=1),
                Order(customer=zhouer, product=products[2], count=2),
                Order(customer=zhouer, product=products[4], count=3),
                Order(customer=zhangsan, product=products[0], count=3),
                Order(customer=zhangsan, product=products[5], count=8),
                Order(customer=zhangsan, product=products[4], count=1),
                Order(customer=lisi, product=products[3], count=7),
                Order(customer=lisi, product=products[5], count=1),
                Order(customer=lisi, product=products[0], count=5),
            ])

    def tearDown(self):
        pass

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
        # .count()获取总行数
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
        # delete会删除queryset的执行结果
        # 当其他对象的外键指向这个被删除的对象，并且外键约束为CASCADE时，此对象也会同步被删除
        deleted, obj = Customer.objects.filter(name='李四').delete()
        self.assertTrue(deleted > 1)
        self.assertIn('app.Order', obj)
        # 查看deleted的值会发现，与Customer关联的Shopping也同时被删除
        queryset = Order.objects.filter(customer__name='李四')
        self.assertFalse(queryset.exists())
        queryset = Customer.objects.filter(name='李四')
        self.assertFalse(queryset.exists())
        # 测试PROTECT
        # 需要注意的是CASCADE和PROTECT都是ORM层面仿真的
        with self.assertRaises(ProtectedError):
            # django.db.models.deletion.ProtectedError
            Supplier.objects.filter(name='桶一食品').delete()

    def test_soft_delete(self):
        """
        软删除处理，通过自定义Manager，在get_queryset的时候，自动添加一个is_deleted=False的过滤条件
        :return:
        """
        # 未被软删除的情况
        self.assertTrue(Product.objects.filter(id=1).exists())
        # 更新is_deleted为True，做软删除
        Product.objects.filter(id=1).update(is_deleted=True)
        # 查询不到任何数据
        self.assertFalse(Product.objects.filter(id=1).exists())
        # 对于get也有效果
        with self.assertRaises(ObjectDoesNotExist):
            product = Product.objects.get(id=1)
            self.assertIsNone(product)

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
            self.assertTrue(isinstance(product, dict))
            # 此时没有 id，只有 product_id 了
            self.assertIn('product_id', product)
        # 外键时，values的值为外键的id(假设id是主键)
        product_list = Product.objects.values('supplier')
        for product in product_list:
            self.assertTrue(isinstance(product, dict))
            # supplier 为 supplier 表的id
            self.assertIn('supplier', product)
            self.assertTrue(isinstance(product['supplier'], int))
        # value和order by一起工作
        product_list = Product.objects.order_by('-id').values()
        self.assertEqual(product_list[0]['id'], len(self.product_list))
        # many to many
        # m2m 会列出所有的组合，比如矿泉水时拥有"食品"和"饮料"两个标签
        # 那么查询出来的结果，矿泉水会出现两次，分别拥有"食品"和"饮料"的标签
        product_list = Product.objects.order_by('id').values('id', 'name', 'tags')
        self.assertTrue(len(product_list) > len(self.product_list))

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
        with transaction.atomic():
            # F对象，使用查询条件中字段的值，参与比较
            # 查询会员价大于零售价的商品，可能是大数据杀熟
            product_list = Product.objects.filter(member_price__gte=F('price')).all()
            assert product_list[0].name
            self.assertEqual(product_list[0].name, '电脑')
            # 电脑涨价
            Product.objects.filter(name='电脑').update(price=F('price')+100)
            Product.objects.filter(name='电脑').update(price=F('price')-99)
            # 需要重新取值，否则内存中的product价格是旧的
            product = Product.objects.get(name='电脑')
            self.assertEqual(product.price, 8000)

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
        # 如果不希望每次查询都使用defer，可以创建同名的model，只要将managed设置为False即可
        from django.db import models

        class ProductNoUpdateTime(BaseModel):

            objects = SoftDelManager()

            name = models.CharField('商品名称', max_length=24)
            price = models.DecimalField('零售价', max_digits=10, decimal_places=6)
            member_price = models.DecimalField('会员价', max_digits=10, decimal_places=6, null=True, blank=True)
            supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT, verbose_name='供应商', null=True, blank=True)

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

    def test_aggregate_annotate(self):
        """
        Django 聚合函数
        aggregate返回的结果为dict，annotate返回的结果为queryset
        :return:
        """
        # Sum等对象的output_field参数可以设置输出的字段类型
        data = Product.objects.aggregate(price=Sum('price', output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(sum((item[2] for item in self.product_list))))
        # Max
        data = Product.objects.aggregate(price=Max('price', output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(max((item[2] for item in self.product_list))))
        # Min
        data = Product.objects.aggregate(price=Min('price', output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(min((item[2] for item in self.product_list))))
        # Avg
        data = Product.objects.aggregate(price=Avg('price', output_field=DecimalField()))
        self.assertEqual(data['price'], Decimal(sum((item[2] for item in self.product_list)) / len(self.product_list)))
        # Count
        # Count还有个参数为distinct，默认为False，当为True时，只统计不重复的数据
        data = Product.objects.aggregate(count=Count('price'))
        self.assertEqual(data['count'], len(self.product_list))
        # 使用 annotate 查询顾客买过的商品总数量
        customer_list = Customer.objects.annotate(count=Sum('order__count')).values()
        for customer in customer_list:
            if customer['count'] is not None:
                self.assertTrue(customer['count'] > 0)
        # 在Sum、Max、Min、Avg、Count等对象中，可以增加filter参数，用于过滤条件
        # 为filter参数赋值一个Q对象，Q对象内接收过滤条件
        # 例如统计所有购买单价在200以上的商品的总数
        customer_list = Customer.objects.annotate(count=Sum('order__count',
                                                            filter=Q(order__product__price__gte=200))
                                                  )
        for customer in customer_list:
            if customer.count is not None:
                self.assertTrue(customer.count > 0)

    def test_contains(self):
        """
        等价于SQL的like "%xxxx%"
        大小写敏感
        :return:
        """
        """
        因为测试的例子中，使用的是SQLite
        在SQLite中，ASCII范围内字符串不区分大小写，ASCII范围之外的字符串，区分大小写
        所以下面的contains和name__icontains实际上是等同的，都不区分大小写
        详见：
        https://docs.djangoproject.com/en/2.0/ref/databases/#sqlite-string-matching
        """
        # 查出所有姓名包含"tom"的顾客
        customer_list = Customer.objects.filter(name__contains='tom').all()
        self.assertTrue(customer_list.count() == 1)
        # 如果需要大小写不敏感，使用icontains
        customer_list = Customer.objects.filter(name__icontains='tom').all()
        self.assertTrue(customer_list.count() == 1)

    def test_in(self):
        """
        等价于SQL的in，可以给in赋值一个可迭代对象，通常是list、tuple或者queryset
        :return:
        """
        customer_list = Customer.objects.filter(id__in=[1, 2, 3, 4])
        self.assertTrue(customer_list.count() == 4)
        # 查询上述客户的购买记录
        order_list = Order.objects.filter(customer__in=customer_list)
        # 基础数据中，每个人有三条购买记录，一共12条
        self.assertTrue(order_list.count() == 12)
        # 如果queryset使用了values(),需要确保values()里只有一个字段的结果
        # 如果有多个字段，会引发TypeError
        with self.assertRaises(TypeError):
            customer_list = Customer.objects.filter(id__in=[1, 2, 3, 4]).values('id', 'name')
            # 查询上述客户的购买记录
            order_list = list(Order.objects.filter(customer__in=customer_list))
            self.assertIsNotNone(order_list)

    def test_select_for_update(self):
        """
        SQLite下无效， 需要mysql
        :return:
        """
        # TODO 待补充完成
        pass

    def test_many_to_many(self):
        """
        测试多对多
        :return:
        """
        # ManyToMany，没有自定义关系表
        # 查询商品的标签
        phone = Product.objects.get(name='手机')
        # tags 属性定义在Product model下，所以可以使用tags.all()获取商品的所有标签
        tags = list(phone.tags.all())
        self.assertTrue(len(tags) == 1)
        # 查询标签下的商品
        tag = Tag.objects.get(name='电子产品')
        # tag 下没有product属性，所以通过product_set获取标签下所有的商品
        products = list(tag.product_set.all())
        self.assertTrue(len(products) > 1)
        # 新增多对多关系
        new_tag = Tag(name='通讯工具')
        # 新增多对多关系中，两个model的实例都必须先save
        new_tag.save()
        # 为手机新增通讯工具的标签
        phone.tags.add(new_tag)
        tags = list(phone.tags.all())
        self.assertTrue(len(tags) == 2)
        # 为食品标签增加冰激凌
        ice_cream = Product(name='冰激凌', price=6, member_price=5)
        # 同样需要save
        ice_cream.save()
        tag = Tag.objects.get(name='食品')
        # 同样使用product_set.add()
        tag.product_set.add(ice_cream)
        products = list(tag.product_set.all())
        self.assertTrue(len(products) == 4)
        # 移除某个多对多的关系，remove接受model或主键
        phone.tags.remove(new_tag)
        # 等同于上面 phone.tags.remove(new_tag.id)
        self.assertTrue(len(phone.tags.all()) == 1)
        # 清除多对多的关系
        phone.tags.clear()
        self.assertTrue(len(phone.tags.all()) == 0)
        # 新增标签除了使用add外，还可以用set批量新增
        tag1 = Tag.objects.get(name='电子产品')
        tag2 = Tag.objects.get(name='通讯工具')
        phone.tags.set([tag1, tag2])
        self.assertTrue(len(phone.tags.all()) == 2)

        # 自定义中间表
        # 通过models.ManyToManyField的through和through_fields自定义中间表
        # add、remove、set都不可用，能使用的只有all()和clear()
        customer = Customer.objects.get(name='张三')
        # 查询客户购买过的商品
        products = customer.products.all()
        self.assertTrue(products.count() == 3)
        # 清除客户与购买商品的关系
        customer.products.clear()
        self.assertTrue(customer.products.count() == 0)

    def test_select_related(self):
        """
        优化外键查询
        :return:
        """
        # 查询商品的供应商名称
        # 这种查询方法效率比较低，需要查询出所有的商品，然后逐一获取商品的supplier外键
        # 在通过外键获取supplier供应商数据，n条商品数据就需要n+1次查询
        product_list = list(Product.objects.all())
        for product in product_list:
            self.assertIsNotNone(product.supplier)
        # 通过select_related进行优化
        product_list = Product.objects.select_related('supplier')
        # 通过join一次查询将供应商信息一并查询出来
        self.assertTrue('JOIN' in str(product_list.query))
        # 再遍历商品数据时，访问商品的供应商数据，不会再触发数据库访问
        for product in product_list.all():
            self.assertTrue(product.supplier)
