import webapp2
import update_schema1
import update_schema2
import update_schema3
import update_schema4
import update_schema5
from google.appengine.ext import deferred

class UpdateHandler1(webapp2.RequestHandler):
    def get(self):
        deferred.defer(update_schema1.UpdateSchema)
        self.response.out.write('Schema migration successfully initiated.')

class UpdateHandler2(webapp2.RequestHandler):
    def get(self):
        deferred.defer(update_schema2.UpdateSchema)
        self.response.out.write('Schema 2 migration successfully initiated.')

class UpdateHandler3(webapp2.RequestHandler):
    def get(self):
        deferred.defer(update_schema3.UpdateSchema)
        self.response.out.write('Schema 3 migration successfully initiated.')

class UpdateHandler4(webapp2.RequestHandler):
    def get(self):
        deferred.defer(update_schema4.UpdateSchema)
        self.response.out.write('Schema 4 migration successfully initiated.')

class UpdateHandler5(webapp2.RequestHandler):
    def get(self):
        deferred.defer(update_schema5.UpdateSchema)
        self.response.out.write('Schema 5 migration successfully initiated.')

app = webapp2.WSGIApplication([('/update_schema1', UpdateHandler1),
	('/update_schema2', UpdateHandler2),
	('/update_schema3', UpdateHandler3),
    ('/update_schema4', UpdateHandler4),
    ('/update_schema5', UpdateHandler5)])