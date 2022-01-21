from django.db import models

# Create your models here.
from apps.users.models import User


class File(models.Model):
    file = models.FileField(upload_to='document/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.file.name
