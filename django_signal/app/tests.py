from django.test import TestCase
from.models import Pizza
from .signals import pizza_done


# Create your tests here.
class SignalTestCase(TestCase):

    def setUp(self):
        pass

    @staticmethod
    def test_post_init():
        article = Pizza(toppings='chicken', size=9)
        article.save()

    def test_sending_signal(self):
        pizza_done.send(self.__class__, toppings='chicken', size=9)

