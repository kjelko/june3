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
    code = self.request.get('code')
    if not code:
      raise NoInvitationSpecifiedError
    invitation = models.Invitation.Get(self.request.get('code'))
    if not invitation:
      raise InvitationNotFoundError
    return invitation.to_dict()
    
  def HandlePost(self):
    return {}



