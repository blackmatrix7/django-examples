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
def save_books(request):
    json_str = '[{"model":"app.book","fields":{"name":"RainbowSix","author":["Tom","Clancy"]}},' \
               '{"model":"app.book","fields":{"name":"NightMoves","author":["Tom","Clancy"]}}]'
    for deserialized_object in serializers.deserialize('json', json_str):
        deserialized_object.save()
    return JsonResponse({'success': True})


def save_books_err(request):
    json_str = '[{"model":"app.book","fields":{"name":null,"author":["Tom","Clancy"]}},' \
               '{"model":"app.book","fields":{"name":null,"author":["Tom","Clancy"]}}]'
    for deserialized_object in serializers.deserialize('json', json_str):
        deserialized_object.save()
    return JsonResponse({'success': True})


def update_books(request):
    json_str = '[{"fields":{"author":1,"name":"Rainbow Six2"},"pk":1,"model":"app.book"},' \
               '{"fields":{"author":1,"name":"Night Moves"},"pk":2,"model":"app.book"}]'
    for deserialized_object in serializers.deserialize('json', json_str):
        deserialized_object.save()
    return JsonResponse({'success': True})


