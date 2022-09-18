from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    my_user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=500, null=False, blank=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task

class AllUsers(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=500)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username