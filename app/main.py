import handlers
import webapp2

class Hello(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<h1>Hello</h1>')


app = webapp2.WSGIApplication([
    ('/', Hello),
], debug=True)
