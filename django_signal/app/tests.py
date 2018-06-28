from django.test import TestCase
from.models import Pizza


# Create your tests here.
class SignalTestCase(TestCase):

    def setUp(self):
        pass

    @staticmethod
    def test_post_init():
        article = Pizza(toppings='test', size=9)
        article.save()
