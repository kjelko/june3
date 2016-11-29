import handlers
import jinja2
import os
import webapp2


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


app = webapp2.WSGIApplication([
    # Main site handlers.
    webapp2.Route('/', WeddingSite),
    webapp2.Route('/api/invitation', handlers.InvitationHandler),
    webapp2.Route('/api/food_choice', handlers.ManageFoodChoiceHandler, methods=['GET']),
    # Admin handlers.
    webapp2.Route('/admin', WeddingAdminSite),
    webapp2.Route('/admin/api/invitation', handlers.ManageInvitationHandler),
    webapp2.Route('/admin/api/food_choice', handlers.ManageFoodChoiceHandler),
], debug=True)
