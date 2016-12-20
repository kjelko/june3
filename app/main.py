import handlers
import jinja2
import os
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import users
from webapp2_extras import routes


IS_DEV = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

APPSPOT_DOMAIN = '%s.appspot.com' % app_identity.get_application_id()

CUSTOM_DOMAIN = 'theelkos.com'

JINJA_ENVIRONMENT = jinja2.Environment(
      autoescape=True,
      extensions=['jinja2.ext.autoescape'],
      loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 
                                                  'static/templates')))


class WeddingSite(webapp2.RequestHandler):
  
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('index.html')
    template_args = {}
    self.response.out.write(template.render(template_args))


class WeddingAdminSite(webapp2.RequestHandler):
  
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('admin.html')
    template_args = {}
    self.response.out.write(template.render(template_args))


class RedirectHandler(webapp2.RedirectHandler):

  def get(self):
    self.redirect('https://%s/s/' % APPSPOT_DOMAIN if not IS_DEV else '/s/')


ROUTES = [ 
    # Main site handlers.
    webapp2.Route('/', RedirectHandler),
    webapp2.Route('/s/', WeddingSite),
    webapp2.Route('/api/invitation', handlers.InvitationHandler),
    webapp2.Route('/api/food_choice', handlers.ManageFoodChoiceHandler, 
                  methods=['GET']),
    # Admin handlers.
    webapp2.Route('/admin', WeddingAdminSite),
    webapp2.Route('/admin/api/invitation', handlers.ManageInvitationHandler),
    webapp2.Route('/admin/api/invitation/bulk',
                  handlers.BulkInvitationHandler),
    webapp2.Route('/admin/api/food_choice', handlers.ManageFoodChoiceHandler),
]


if IS_DEV:
  app = webapp2.WSGIApplication(ROUTES, debug=True)
else:
  app = webapp2.WSGIApplication([
      routes.DomainRoute('<:(www.%s|%s)>' % (CUSTOM_DOMAIN, CUSTOM_DOMAIN), [
          webapp2.Route('/', RedirectHandler)
      ]),
      routes.DomainRoute(APPSPOT_DOMAIN, ROUTES)
  ])
