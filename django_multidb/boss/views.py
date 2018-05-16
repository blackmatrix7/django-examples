from .models import Boss
from django.shortcuts import HttpResponse


# Create your views here.
def add_boss(request):
    Boss(name=request.GET['name'], age=request.GET['age']).save()
    return HttpResponse('success')
