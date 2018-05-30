from .models import Customer
from django.test import TestCase


# Create your tests here.
class StudentTestCase(TestCase):

    def setUp(self):
        pass

    def test_add_customer(self):
        """
        Django ORM 新增
        :return:
        """
        customer = Customer(name='王五', age=56)
        customer.save()
        self.assertEqual(customer.name, '王五')

    def tearDown(self):
        pass
