from django.conf import settings

from google.appengine.ext import db as models

from appengine_django.models import BaseModel

class Point(BaseModel):
  nick = models.StringProperty()
  created_at = models.DateTimeProperty(auto_now_add=True)
  comment = models.TextProperty()
  by_user = models.UserProperty()
  value = models.IntegerProperty()

class Total(BaseModel):
  nick = models.StringProperty()
  total = models.IntegerProperty()

class TotalByVoter(BaseModel):
  nick = models.StringProperty()
  total = models.IntegerProperty()
  voter = models.UserProperty()
