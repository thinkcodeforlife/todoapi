from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    title = models.CharField(max_length=80, blank=False)
    content = models.CharField(max_length=500, blank=False)
    user = models.ForeignKey(User, related_name='todos', on_delete=models.CASCADE, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    is_finished = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Todo=(id:{self.id} | Title:'{self.title}' | User: '{self.user.username}')" 

    class Meta:
        ordering = ('-updated_at',)
