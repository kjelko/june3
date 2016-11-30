import handlers
import jinja2
import os
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import users
from webapp2_extras import routes


JINJA_ENVIRONMENT = jinja2.Environment(
      autoescape=True,
      extensions=['jinja2.ext.autoescape'],
      loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 
                                                  'static/templates')))


class WeddingSite(webapp2.RequestHandler):
  
  def get(self):
    if users.is_current_user_admin():
      template = JINJA_ENVIRONMENT.get_template('index.html')
      template_args = {}
      self.response.out.write(template.render(template_args))
    else:
      self.response.out.write('<a href="%s">login</a>' % users.create_login_url())

class WeddingAdminSite(webapp2.RequestHandler):
  
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('admin.html')
    template_args = {}
    self.response.out.write(template.render(template_args))


class RedirectHandler(webapp2.RedirectHandler):

  def get(self):
    self.redirect('https://%s.appspot.com' % app_identity.get_application_id())


app = webapp2.WSGIApplication([
    routes.DomainRoute('theelkos.com', [webapp2.Route('/', RedirectHandler)]),

    # Main site handlers.
    webapp2.Route('/', WeddingSite),
    webapp2.Route('/api/invitation', handlers.InvitationHandler),
    webapp2.Route('/api/food_choice', handlers.ManageFoodChoiceHandler, methods=['GET']),
    # Admin handlers.
    webapp2.Route('/admin', WeddingAdminSite),
    webapp2.Route('/admin/api/invitation', handlers.ManageInvitationHandler),
    webapp2.Route('/admin/api/food_choice', handlers.ManageFoodChoiceHandler),
], debug=True)
