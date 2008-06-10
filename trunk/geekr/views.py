from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

import simplejson

from google.appengine.api import users
from google.appengine.ext import db

from geekr.models import Point, Total

def index(request):
  out = {'recent_points': []}

  query = db.Query(Point).order('-created_at')
  points = query[:50]
  for p in points:
    out['recent_points'].append({'nick': p.nick,
                'value': p.value,
                'comment': p.comment,
                'created_at': p.created_at.isoformat(),
                'by_user': p.by_user.nickname()
                })

  return HttpResponse(simplejson.dumps(out, indent=2))

def score(request, nick):
  total = Total.get_by_key_name(nick)
  
  if not total:
    score = 0
  else:
    score = total.total

  out = {'score': score,
         'nick': nick}
  return HttpResponse(simplejson.dumps(out, indent=2))

def verbose(request, nick):

  total = Total.get_by_key_name(nick)
  if not total:
    score = 0
  else:
    score = total.total

  query = db.Query(Point).filter('nick =', nick).order('-created_at')
  
  out = {'nick': nick,
         'score': score,
         'points': [],
         }
  for p in query:
    out['points'].append({'nick': p.nick,
                'value': p.value,
                'comment': p.comment,
                'created_at': p.created_at.isoformat(),
                'by_user': p.by_user.nickname()
                })
  return HttpResponse(simplejson.dumps(out, indent=2))

def inc(request, nick, value, after=False):
  comment = request.REQUEST.get('comment', None)

  new_value = increment_safely(nick, value=value, comment=comment, after=after)

  out = {'nick': nick,
         'score': new_value
         }

  return HttpResponse(simplejson.dumps(out, indent=2))

def increment_safely(nick, value=1, comment=None, after=False):

  user = users.get_current_user()

  params = {'nick': nick,
            'by_user': user,
            'value': value,
            }

  if comment:
    params['comment'] = comment

  total = Total.get_or_insert(nick, nick=nick, total=0)
  if not after:
    old_value = total.total

  def _increment(total, nick, value, params, after=False):

    # create a new point, update the total
    point = Point(parent=total, **params)
    point.put()
  
    total.total += value
    total.put()

    return total.total

  new_value = db.run_in_transaction(_increment, total, nick, value, 
                                    params, after)
  if after:
    return new_value
  else:
    return old_value
