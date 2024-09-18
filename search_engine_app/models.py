from django.db import models
# models.py
from mongoengine import Document, StringField


class SearchResult(Document):
    name = StringField()
    description = StringField()
    link = StringField()

# Create your models here.
