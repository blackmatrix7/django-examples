from django.db import models

# Create your models here.


class Article(models.Model):

    title = models.CharField('标题', max_length=128)
    content = models.TextField('内容')
