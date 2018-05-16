"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from boss.views import add_boss
from client.views import add_client
from driver.views import add_driver
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_boss/', add_boss),
    path('add_driver/', add_driver),
    path('add_client/', add_client),
]
