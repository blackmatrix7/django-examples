from .models import Client
from django.shortcuts import HttpResponse


# Create your views here.
def add_client(request):
    Client(name=request.GET['name'], age=request.GET['age']).save()
    return HttpResponse('success')
