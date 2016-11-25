import handlers
import jinja2
import os
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
      autoescape=True,
      extensions=['jinja2.ext.autoescape'],
      loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


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
    webapp2.Route('/', WeddingSite),
    webapp2.Route('/api/invitation', handlers.InvitationHandler),
    webapp2.Route('/admin', WeddingAdminSite),
    webapp2.Route('/admin/api/invitation', handlers.ManageInvitationHandler),
], debug=True)
