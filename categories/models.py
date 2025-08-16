from django.db import models
from tasks.models import Task

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tasks = models.ManyToManyField(Task, related_name="categories", blank=True)

    def __str__(self):
        return self.name
