from django.db import models


class Person(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    birthdate = models.DateField()

    def natural_key(self):
        return [self.first_name, self.last_name]

    class Meta:
        unique_together = (('first_name', 'last_name'),)


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
