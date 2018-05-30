from .models import *
from django.http import JsonResponse
from django.forms.models import model_to_dict

# Create your views here.


def shopping_list(request):
    customer_id = request.GET.dict()['customer_id']
    model_list = Shopping.objects.filter(customer__id=customer_id).values('customer__customer_name', 'count',
                                                                          'product__product_name', 'product__price').all()
    return JsonResponse([model for model in model_list], safe=False)


def customer_products(request):
    customer = Customer.objects.get(id=1)
    products = customer.products.all()
    return JsonResponse([model_to_dict(product) for product in products], safe=False)


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



