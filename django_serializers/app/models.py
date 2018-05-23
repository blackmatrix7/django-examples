from django.db import models


class Person(models.Model):

    class Meta:
        unique_together = (('first_name', 'last_name'),)

    birthdate = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def natural_key(self):
        return [self.first_name, self.last_name]


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
