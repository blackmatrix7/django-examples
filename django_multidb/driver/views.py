from .models import Driver
from django.shortcuts import HttpResponse


# Create your views here.
def add_driver(request):
    Driver(name=request.GET['name'], age=request.GET['age']).save()
    return HttpResponse('success')
