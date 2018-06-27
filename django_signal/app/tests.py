from django.test import TestCase
from.models import Article


# Create your tests here.
class SignalTestCase(TestCase):

    def setUp(self):
        pass

    @staticmethod
    def test_post_init():
        article = Article(title='test', content='test')
        article.save()
