import json
from .models import Book
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def get_books(request):
    book = Book.objects.all()
    json_str = serializers.serialize('json', book, )
    return JsonResponse({'books': json.loads(json_str)})


# Create your views here.
@csrf_exempt
def set_books(request):
    body = request.body.decode()
    json_str = serializers.deserialize('json', body)
    return JsonResponse({'books': json.loads(json_str)})



