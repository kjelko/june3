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
