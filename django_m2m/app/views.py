from .models import *
from django.http import JsonResponse

# Create your views here.


def get_customer_products(request):
    customer_id = request.GET.dict()['customer_id']
    model_list = Order.objects.filter(customer__id=customer_id).values('customer__customer_name', 'count',
                                                                       'product__product_name', 'product__price').all()
    return JsonResponse([model for model in model_list], safe=False)
