import webapp2

class Hello(webapp2.RequestHandler):
  def get(self):
    print '<h1>Hello</h1>'

app = webapp2.WSGIApplication([
    ('/', Hello),
], debug=True)
