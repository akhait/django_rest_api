import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Article(models.Model):
    ''' Represents an article. '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=60)  # article title
    pub_date = models.DateTimeField(auto_now_add=True)  # date added
    mod_date = models.DateTimeField(auto_now=True)  # date modified
    author = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)  # author

    def __str__(self):
        return self.title


class Sentence(models.Model):
    ''' Represents an article's sentence. '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, related_name='sentences', on_delete=models.CASCADE)
    num = models.IntegerField(default=1, blank=True)
    text = models.TextField()  # sentence text
    pub_date = models.DateTimeField(auto_now_add=True)  # date added
    mod_date = models.DateTimeField(auto_now=True)  # date last modified
    author = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)  # user that added a sentence
   
    class Meta:
        unique_together = ('article', 'num')
        ordering = ['num']

    def __str__(self):
        return self.text
