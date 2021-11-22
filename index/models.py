from django.db import models

class File(models.Model):
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to='file/')

    def __str__(self):
        return self.title
