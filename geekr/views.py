from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

import simplejson

from google.appengine.api import users
from google.appengine.ext import db

from geekr.models import Point, Total, TotalByVoter

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
  out['commands'] = {'plusplus_nick': '/++%(nick)s',
                     'nick_plusplus': '/%(nick)s++',
                     'minusminus_nick': '/--%(nick)s',
                     'nick_minusminus': '/%(nick)s--',
                     'score_nick': '/%(nick)s',
                     'score_nick_verbose': '/%(nick)s/verbose',
                     'score_nick_by_voter': '/%s(nick)s/by_voter'}

  return HttpResponse(simplejson.dumps(out, indent=2))

def score(request, nick):
  total = Total.get_or_insert(nick, nick=nick, total=0)
  
  score = total.total

  out = {'score': score,
         'nick': nick}
  return HttpResponse(simplejson.dumps(out, indent=2))

def scoreboard(request):
  query = db.Query(Total).order('-total')
  results = query.fetch(10)

  out = {'top_scorers': []}
  for p in results:
    out['top_scorers'].append({'nick': p.nick,
                               'total': p.total})

  return HttpResponse(simplejson.dumps(out, indent=2))

def verbose(request, nick):
  total = Total.get_or_insert(nick, nick=nick, total=0)
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
                'by_user': _display_nick(p.by_user)
                })
  return HttpResponse(simplejson.dumps(out, indent=2))

def verbose_by_voter(request, nick):
  total = Total.get_or_insert(nick, nick=nick, total=0)
  score = total.total
  
  if 'build' in request.GET:
    _rebuild_total_by_voters(total, nick)
  
  query = db.Query(TotalByVoter).filter('nick =', nick)
  
  out = {'nick': nick,
         'score': score,
         'voters': [],
         }
  for p in query:
    out['voters'].append({'voter': _display_nick(p.voter),
                         'total': p.total})
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

  by_voter_key = '%s/%s' % (nick, user.nickname())
  by_voter = TotalByVoter.get_or_insert(by_voter_key, nick=nick, total=0, 
                                        voter=user, parent=total)

  if not after:
    old_value = total.total

  def _increment(total, nick, value, params, after=False):

    # create a new point, update the total
    point = Point(parent=total, **params)
    point.put()
    
    by_voter.total += value
    by_voter.put()

    total.total += value
    total.put()

    return total.total

  new_value = db.run_in_transaction(_increment, total, nick, value, 
                                    params, after)
  if after:
    return new_value
  else:
    return old_value


def _display_nick(user):
  nickname = user.nickname()
  nickname = nickname.split('@')[0]
  return nickname

def _rebuild_total_by_voters(total, nick):
  totals_query = db.Query(TotalByVoter).filter('nick =', nick)
  for t in totals_query:
    t.delete()

  query = db.Query(Point).filter('nick =', nick).order('-created_at')
  totals = {}
  for p in query:
    total_key = '%s/%s' % (nick, p.by_user.nickname())
    totals.setdefault(total_key, 
                      [nick, p.by_user, 0])
    totals[total_key][2] += p.value
  for k, v in totals.iteritems():
    t = TotalByVoter(key_name = k, nick= v[0], 
                     voter=v[1], total=v[2], parent=total)
    t.put()

