from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    User = get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, blank=True, null=True)
    categories = models.ManyToManyField('categories.Category', related_name="tasks", blank=True)
    tags = models.ManyToManyField('tags.Tag', related_name="tasks", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
