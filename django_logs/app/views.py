from logger import logger
from django.shortcuts import HttpResponse


# Create your views here.

def test_logger(request):
    assert request
    logger.info('test log')
    result = 1/0
    return HttpResponse('test log')
