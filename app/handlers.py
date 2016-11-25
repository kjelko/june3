import httplib
import json
import models
import webapp2


class Error(Exception):
  default_msg = 'An unknown error occured.'
  code = httplib.INTERNAL_SERVER_ERROR

  def __init__(self, msg=None):
    super(Error, self).__init__(msg or self.default_msg)


class NoInvitationSpecifiedError(Error):
  default_msg = 'No invitation code was specified.'
  code = httplib.BAD_REQUEST


class InvitationNotFoundError(Error):
  default_msg = 'Could not find invitation with specified code.'
  code = httplib.NOT_FOUND


class FoodChoiceNotFoundError(Error):
  default_msg = 'Could not find food choice with specified code.'
  code = httplib.NOT_FOUND


class InvalidRequestError():
  default_msg = ''


class JsonHandler(webapp2.RequestHandler):
  """Base JSON handler."""

  def __init__(self, *args, **kwargs):
    super(JsonHandler, self).__init__(*args, **kwargs)
    self.get = self.GetHandler('get')
    self.post = self.GetHandler('post')

  def GetHandler(self, method):
    def __handler__(*args, **kwargs):
      self.DoHandler(method, *args, **kwargs)
    return __handler__

  def DoHandler(self, method, *args, **kwargs): 
    resp = None   
    handler_method = getattr(self, 'Handle%s' % method.title())
    
    if handler_method: 
      try:  
        resp = handler_method(*args, **kwargs)
      except Error as e:
        resp = {'error': str(e)}
        self.response.status = e.code
      except Exception as e:
        self.response.status = httplib.INTERNAL_SERVER_ERROR
        resp = {'error': str(e)}
    else:
      self.response.status = 501
    
    self.response.headers['Content-type'] = 'application/json'
    if resp:
      self.response.out.write(json.dumps(resp))


class InvitationHandler(JsonHandler):
  """Retrieves invitation details."""

  def HandleGet(self):
    """Retreives ingormations about a single invitation.

    GET Args:
      code: The unique invitation code.
    Returns:
      invitation information
    """
    code = self.request.get('code')
    if not code:
      raise NoInvitationSpecifiedError
    return GetInvitation(code).to_dict()
 

def GuestHandler(JsonHandler):

  def HandlePost(self):
    """Updates RSVP status and food choice.

    POST Args:
      code: Invitation code.
      rsvp: RSVP status.
      guests_attending: Number of guests attending.
    Returns:
      updated invitation info.
    """
    code = self.request.get('code')
    if not code:
      raise NoInvitationSpecifiedError
    invitation = GetInvitation(code)
    
    invitation_guest_ids = [g.key.id() for g in invitation.guests]

    if self.request.get('guest'):
      raise GuestNotSpecifiedError

    guest = model.Guest.get_by_id(int(self.request.get('guest')))

    rsvp = self.request.get('rsvp')
    
    if rsvp == models.RsvpStatus.COMING
      guest.rsvp = models.RsvpStatus.COMING
      quest.food_choice = ndb.Key(model.FoodChoice, 
                                  int(self.request.get('food_choice')))
    
    elif rsvp == models.RsvpStatus.NOT_COMING:
      invitation.rsvp = models.RsvpStatus.NOT_COMING
      guest.food_choice = None
    
    guest.put()
    return guest.to_dict()


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
    GetInvitation(self.request.get('code')).key.delete()


class ManageFoodChoiceHandler(JsonHandler):

  def HandleGet(self):
    food_choice_id = self.request.get('food_choice_id')
    if food_choice_id:
      return GetFoodChoice(food_choice_id).to_dict()
    else:
      return [f.to_dict() for f in models.FoodChoice.query().iter()]

  def HandlePost(self):
    food_choice_id = self.request.get('food_choice_id')
    food_choice = (GetInvitation(food_choice_id) if food_choice_id else
                   models.FoodChoice())
    food_choice.name = self.request.get('name')
    food_choice.name = self.request.get('description')
    food_choice.put()

  def HandleDelete(self):
    food_choice_key = GetFoodChoice(self.request.get('food_choice_id')).key
    q = models.Guest.query().filter(models.Guest.food_choice == )
    for guest in q.iter():
      guest.food_choice = None
      guest.put()
    food_choice_key.delete()

def GetFoodChoice(food_choice_id):
  food_choice = models.FoodChoice.get_by_id(AsInt(food_choice_id))
  if not food_choice:
    raise InvitationNotFoundError


def GetInvitation(code):
  invitation = models.Invitation.Get(code)
  if not invitation:
    raise InvitationNotFoundError


def AsInt(value):
  try:
    return int(value)
  except ValueError:
    raise InvalidRequestError
