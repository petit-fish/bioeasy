from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import redirect


class Post(models.Model):
    title = models.CharField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish = models.DateTimeField(default=datetime.now())
    base_id = models.CharField(max_length=20)
    body = models.TextField()
    base_title = models.CharField(max_length=500)

    def __str__(self):
        return self.title + ' | ' + str(self.author)

    def get_absolute_url(self):
        return redirect('post_list')


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date_added = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)


class Memo(models.Model):
    body = models.TextField()
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    pmc_id = models.CharField(max_length=20)

    def __str__(self):
        return self.pmc_id + '|' + str(self.name)


class Image(models.Model):
    pmc_id = models.CharField(max_length=20)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.pmc_id + 'image'
