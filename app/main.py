import handlers
import jinja2
import os
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
      autoescape=True,
      extensions=['jinja2.ext.autoescape'],
      loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Hello(webapp2.RequestHandler):
  def get(self):
    self.response.out.write()


app = webapp2.WSGIApplication([
    webapp2.Route('/', Hello),
    webapp2.Route('/api/invitation', handlers.InvitationHandler)
], debug=True)
