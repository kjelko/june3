import csv
import httplib
import json
import logging
import models
import urllib
import webapp2

from google.appengine.api import memcache
from google.appengine.api import urlfetch


class Error(Exception):
  default_msg = 'An unknown error occured.'
  code = httplib.INTERNAL_SERVER_ERROR

  def __init__(self, msg=None):
    super(Error, self).__init__(msg or self.default_msg)


class NoInvitationSpecifiedError(Error):
  default_msg = 'No invitation code was specified.'
  code = httplib.BAD_REQUEST


class ExpiredTokenError(Error):
  default_msg = 'Token expired. Please refresh and try again.'
  code = httplib.FORBIDDEN


class CaptchaError(Error):
  default_msg = 'reCaptcha error'
  code = httplib.BAD_REQUEST


class GuestNotOnInvitationError(Error):
  default_msg = 'Guest is not on invitation.'
  code = httplib.BAD_REQUEST


class InvitationNotFoundError(Error):
  default_msg = 'Could not find invitation with specified code.'
  code = httplib.NOT_FOUND


class FoodChoiceNotFoundError(Error):
  default_msg = 'Could not find food choice with specified code.'
  code = httplib.NOT_FOUND


class NoFoodChoiceSelectionError(Error):
  default_msg = 'Please select a food choice.'
  code = httplib.BAD_REQUEST


class InvalidRequestError():
  default_msg = ''


class JsonHandler(webapp2.RequestHandler):
  """Base JSON handler."""

  def __init__(self, *args, **kwargs):
    super(JsonHandler, self).__init__(*args, **kwargs)
    self.get = self.GetHandler('get')
    self.post = self.GetHandler('post')
    self.delete = self.GetHandler('delete')

  def GetHandler(self, method):
    def __handler__(*args, **kwargs):
      self.DoHandler(method, *args, **kwargs)
    return __handler__

  def DoHandler(self, method, *args, **kwargs): 
    resp = None   
    handler_method = getattr(self, 'Handle%s' % method.title())

    if handler_method:
      if method == 'post':
        try:
          request = json.loads(self.request.body or '')
        except ValueError:
          request = {}
        for key, list_value in self.request.POST.dict_of_lists().iteritems():
          request[key] = list_value[0] if len(list_value) == 1 else list_value
        self.request = request
      try:
        resp = handler_method(*args, **kwargs)
      except Error as e:
        resp = {'error': str(e)}
        self.response.status = e.code
      except Exception as e:
        logging.exception('Uncaught error.')
        self.response.status = httplib.INTERNAL_SERVER_ERROR
        resp = {'error': str(e)}
    else:
      self.response.status = 501
    
    if resp:
      self.response.headers['Content-type'] = 'application/json'
      self.response.out.write(json.dumps(resp))


class InvitationHandler(JsonHandler):
  """Retrieves invitation details."""

  def HandleGet(self):
    """Retreives ingormations about a single invitation.

    GET Args:
      g-recaptcha-response: reCaptcha response.
      code: The unique invitation code.
    Returns:
      invitation information
    """
    repsonse = {}
    try:
      g_captcha_response = self.request.get('g-recaptcha-response')
      form_data = urllib.urlencode({
          'secret': '6Lc1Rw0UAAAAAMun0dm6SQd0PdCuPIcYb4YwW0Rg',
          'response': g_captcha_response,
          'remoteip': self.request.remote_addr 
      })
      result = urlfetch.fetch(
          url='https://www.google.com/recaptcha/api/siteverify',
          payload=form_data,
          method=urlfetch.POST,
          headers={'Content-Type': 'application/x-www-form-urlencoded'})
      response = json.loads(result.content)
    except Exception:
      logging.exception('reCAPTCHA error.')
      raise CaptchaError

    if not response.get('success'):
      logging.error('reCAPTCHA not successfull: %s.', result.content)
      raise CaptchaError

    code = self.request.get('code')
    memcache.add(g_captcha_response, code, 600)
    if not code:
      raise NoInvitationSpecifiedError
    return GetInvitation(code).to_dict()

  def HandlePost(self):
    """Updates RSVP status and food choice.

    POST Args:
      code: Invitation code.
      guests: Guest info.
    Returns:
      updated invitation info.
    """
    updated_invitation = self.request.get('invitation', {})
    code = updated_invitation.get('code')
    if not code:
      raise NoInvitationSpecifiedError

    if memcache.get(self.request.get('token', '')) != code:
      logging.error('Expired token')
      raise ExpiredTokenError

    invitation = GetInvitation(code)

    invitation_guest_ids = [g.id() for g in invitation.guests]

    if not updated_invitation.get('guests'):
      raise GuestNotSpecifiedError

    for guest in updated_invitation.get('guests'):

      if guest.get('id') not in invitation_guest_ids:
        raise GuestNotOnInvitationError

      guest_ndb = models.Guest.get_by_id(guest.get('id'))
      rsvp = guest.get('rsvp')
      
      if rsvp == models.RsvpStatus.COMING:
        guest_ndb.rsvp = models.RsvpStatus.COMING
        if not guest.get('food_choice'):
          raise NoFoodChoiceSelectionError
        guest_ndb.food_choice = models.FoodChoice(
            id=guest.get('food_choice').get('id')).key
      
      elif rsvp == models.RsvpStatus.NOT_COMING:
        guest_ndb.rsvp = models.RsvpStatus.NOT_COMING
        guest_ndb.food_choice = None
      
      guest_ndb.put()


class ManageInvitationHandler(JsonHandler):
  """Allows admins to manage invitations."""

  def HandleGet(self):
    """Returns info about a single or list of invitations.
    
    GET Args:
      code: Id of the invitation to list. If not specified all are returned.
    Returns:
      The requested invitation info.
    """
    code = self.request.get('code')
    if code:
      return GetInvitation(code).to_dict()
    else:
      return [i.to_dict() for i in models.Invitation.query().iter()]

  def HandlePost(self):
    """Updated invations/guests.

    POST Args:
      code: The code of the invitation to updated. If not specified a new one
          will be created.
      guests: List of guest information to attach to the invitation.
    Returns:
      Updated invitation.
    """
    code = self.request.get('code')
    invitation = GetInvitation(code) if code else models.Invitation.Create()
    invitation.guests = []

    guests = json.parse(self.request.get('guests'))
    for g in guest:
      guest_id = g.get('id')
      guest = model.Guest.get_by_id(guest_id) if guest_id else model.Guest()
      if g.get('rsvp') == models.RsvpStatus.COMING:
        guest.rsvp = models.RsvpStatus.COMING
        guest.food_choice = ndb.Key(model.FoodChoice, int(g.get('food_choice')))
      elif g.get('rsvp') == models.RsvpStatus.NOT_COMING:
        guest.rsvp = models.RsvpStatus.NOT_COMING
        guest.food_choice = None
      else:
        guest.rsvp == models.RsvpStatus.NO_RESPONSE
        guest.food_choice = None
      invitation.guests.append(guest.put())

    invitation.put()
    return invitation.to_dict()  

  def HandleDelete(self):
    invitation = GetInvitation(self.request.get('code'))
    for guest in invitation.guests:
      guest.key.delete()
    invitation.key.delete()


class BulkInvitationHandler(JsonHandler):
  """Handles bulk csv upload of guests."""

  def HandleGet(self):
    """Produces a downloadable csv file of guests."""
    self.response.headers['Content-type'] = 'text/csv'
    food_choices = list(models.FoodChoice.query().fetch())
    fieldnames = ['GUEST NAME'] + [f.name for f in food_choices]
    csv_writer = csv.DictWriter(self.response.out, fieldnames=fieldnames)
    csv_writer.writeheader()
    for invitation in models.Invitation.query().iter():
      guests = [g.get() for g in invitation.guests]
      row = {'GUEST NAME': ' & '.join([g.name for g in guests])}
      for food_choice in food_choices:
        row[food_choice.name] = len(
              [g for g in guests if g.food_choice == food_choice.key])
      csv_writer.writerow(row)

  def HandlePost(self):
    """Parses a csv file and creates invitations.

    CSV file should be in the following form:

    guest_name_1, guest_name_2
    guest_name_3
    guest_name_4, guest_name_5, guest_name_6

    POST Args:
      csv: The csv file to parse.
    """
    csv_rows = csv.reader(self.request.get('csv').file)
    for row in csv_rows:
      print row
      if row:
        invitation = models.Invitation.Create()
        print invitation
        for guest_name in row:
          if guest_name:
            invitation.guests.append(models.Guest(name=guest_name).put())
        print invitation
        invitation.put()


class ManageFoodChoiceHandler(JsonHandler):

  def HandleGet(self):
    food_choice_id = self.request.get('id')
    if food_choice_id:
      return GetFoodChoice(food_choice_id).to_dict()
    else:
      return [f.to_dict() for f in models.FoodChoice.query().iter()]

  def HandlePost(self):
    food_choice_id = self.request.get('id')
    food_choice = (GetFoodChoice(food_choice_id) if food_choice_id else
                   models.FoodChoice())
    food_choice.name = self.request.get('name')
    food_choice.description = self.request.get('description')
    food_choice.put()
    return food_choice.to_dict()

  def HandleDelete(self):
    food_choice_key = GetFoodChoice(self.request.get('id')).key
    q = models.Guest.query().filter(models.Guest.food_choice == food_choice_key)
    for guest in q.iter():
      guest.food_choice = None
      guest.put()
    food_choice_key.delete()


def GetFoodChoice(food_choice_id):
  print food_choice_id
  food_choice = models.FoodChoice.get_by_id(AsInt(food_choice_id))
  if not food_choice:
    raise FoodChoiceNotFoundError
  return food_choice


def GetInvitation(code):
  invitation = models.Invitation.Get(code.upper())
  if not invitation:
    raise InvitationNotFoundError
  return invitation


def AsInt(value):
  try:
    return int(value)
  except ValueError:
    raise InvalidRequestError
