import json
from .models import Book
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def get_books(request):
    book = Book.objects.all()
    json_str = serializers.serialize('json', book, use_natural_foreign_keys=True)
    return JsonResponse(json.loads(json_str), safe=False)


@csrf_exempt
def set_books(request):
    for deserialized_object in serializers.deserialize('json', request.body.decode()):
        deserialized_object.save()
    return JsonResponse({'success': True})



