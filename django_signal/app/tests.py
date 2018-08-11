from django.test import TestCase
from.models import Pizza
from .signals import pizza_done, close_store, open_store
from .receivers import receiver_pizza_done


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

    def test_sending_two_signals(self):
        open_store.send(self.__class__)
        close_store.send(self.__class__, turnover=20000)

    def test_disconnect_signal(self):
        # 使用disconnect断开接收器和消息的连接，成功断开返回True
        self.assertTrue(pizza_done.disconnect(dispatch_uid='pizza_done'))

