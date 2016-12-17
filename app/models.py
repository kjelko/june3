import random
import string

from google.appengine.ext import ndb


class JsonMixin(object):

  def to_dict(self):
    d = {}
    if isinstance(self, ndb.Model):
      d['id'] = self.key.id()
    for key, prop in self._properties.iteritems():
      value = getattr(self, key)
      if isinstance(prop, ndb.KeyProperty) and value:
        if isinstance(value, list):
          d[key] = []
          for v in value:
            model_instance = v.get()
            if model_instance:
              d[key].append(model_instance.to_dict()) 
        else:
          model_instance = value.get()
          d[key] = model_instance.to_dict() if model_instance else None
      else:
        d[key] = value
    return d


class RsvpStatus(object):
  NO_RESPONSE = 'no_response'
  COMING = 'coming'
  NOT_COMING = 'not_coming'


class FoodChoice(JsonMixin, ndb.Model):
  name = ndb.StringProperty()
  description = ndb.StringProperty()


class Guest(JsonMixin, ndb.Model):
  name = ndb.StringProperty(default='Guest')
  food_choice = ndb.KeyProperty(kind=FoodChoice)
  rsvp = ndb.StringProperty(default=RsvpStatus.NO_RESPONSE)
  dietary_notes = ndb.StringProperty()


class Invitation(JsonMixin, ndb.Model):
  code = ndb.StringProperty()
  guests = ndb.KeyProperty(kind=Guest, repeated=True)

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


class Wedding(JsonMixin, ndb.Model):
  """Ancestor for invitation."""
_WEDDING = Wedding.get_or_insert('wedding')


def _GenerateUid():
  n = random.choice([5, 6])
  return ''.join(random.choice(string.ascii_uppercase) for _ in range(n))
