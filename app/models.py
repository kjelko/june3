import random
import string

from google.appengine.ext import ndb


class RsvpStatus(object):
  NO_RESPONSE = 'no_response'
  COMING = 'coming'
  NOT_COMING = 'not_coming'


class FoodChoice(ndb.Model):
  name = ndb.StringProperty()
  description = ndb.StringProperty()


class Guest(ndb.Model):
  name = ndb.StringProperty()
  food_choice = ndb.KeyProperty(kind=FoodChoice)


class Invitation(ndb.Model):
  code = ndb.StringProperty()
  guests = ndb.KeyProperty(kind=Guest, repeated=True)
  rsvp = ndb.StringProperty(default=RsvpStatus.NO_RESPONSE)

  @classmethod
  def Get(cls, code, keys_only=False):
    return cls.query(ancestor=_WEDDING.key).filter(
        cls.code == code).get(keys_only=keys_only)

  @classmethod
  @ndb.transactional
  def Create(cls):
    code = _GenerateUid()
    while cls.Get(code, keys_only=True) is not None:
      code = _GenerateUid()

    inviation = cls(parent=_WEDDING.key, code=code)
    inviation.put()
    return inviation


class Wedding(ndb.Model):
  """Ancestor for invitation."""
_WEDDING = Wedding.get_or_insert('wedding')


def _GenerateUid():
  n = random.choice([5, 6])
  return ''.join(random.choice(string.ascii_uppercase) for _ in range(n))
