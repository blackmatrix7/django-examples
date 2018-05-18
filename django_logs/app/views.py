from logger import logger
from django.shortcuts import HttpResponse


# Create your views here.

def test_logger(request):
    logger.info('test log')
    return HttpResponse('test log')
