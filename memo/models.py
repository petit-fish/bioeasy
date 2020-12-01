from django.db import models
from django.contrib.auth.models import User


class Bookmark(models.Model):
    site_name = models.CharField(max_length=500)
    url = models.URLField('Site URL')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return " contents: " + self.site_name + ", url: " + self.url
        # 객체를 출력할 때 나타나는 값
