from django.test import TestCase
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import Snippet
from .serializers import SnippetSerializer

# Create your tests here.


class SnippetsTestCase(TestCase):

    def setUp(self):
        self.snippet_a = Snippet(code='foo = "bar"\n')
        self.snippet_a.save()
        self.snippet_b = Snippet(code='print "hello, world"\n')
        self.snippet_b.save()

    def test_serializing_deserialization(self):
        # 序列化
        serializer = SnippetSerializer(self.snippet_a)
        self.assertIsNotNone(serializer.data)
        content = JSONRenderer().render(serializer.data)
        self.assertIsNotNone(content)
        # 反序列化
        stream = BytesIO(content)
        data = JSONParser().parse(stream)
        # data['linenos'] = True
        self.assertIsNotNone(data)
        serializer = SnippetSerializer(data=data)
        # 验证数据
        serializer.is_valid()
        self.assertIsNotNone(serializer.validated_data)
        # obj = serializer.save()
        # obj.save()
        # self.assertTrue(Snippet.objects.get(id=1).linenos)

    def tearDown(self):
        pass
