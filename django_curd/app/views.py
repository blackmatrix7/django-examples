from .models import *
from django.http import JsonResponse
from django.forms.models import model_to_dict

# Create your views here.


def customer_products(request):
    """
    查询某个客户所有购买过的商品和数量
    :param request:
    :return:
    """
    customer = Customer.objects.get(id=1)
    return JsonResponse([model_to_dict(product) for product in customer.products.all()], safe=False)


def change(request):
    customer = Customer.objects.get(id=1)
    # 自定义中间表时，add方法不可用，因为中间表可能会有其他字段
    # 比如中间表Shopping增加count字段
    # customer.products.add(1)
    # 同样的，set方法也不可用
    # AttributeError
    # Cannot set values on a ManyToManyField which specifies an intermediary model. Use app.Shopping's Manager instead.
    # customer.products.set([1, 2, 3])
    # remove也是不可用的
    # customer.products.remove(1)



