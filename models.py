from django.db import models
from oauth import oauth
import re, httplib, simplejson
from utils import *

class User(models.Model):
	username = models.CharField(max_length=40)
	email = models.EmailField()
	oauth_token = models.CharField(max_length=200)
	oauth_token_secret = models.CharField(max_length=200)

	def validate(self):
		errors = []
		if self.username and not re.compile('^[a-zA-Z0-9_]{1,40}$').match( \
			self.username):
			errors += ['username']
		if self.email and not re.compile( \
			'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$').match( \
			self.email):
			errors += ['email']
		return errors

	# django.core.context_processors.auth assumes that an object attached
	# to request.user is always a django.contrib.auth.models.User, which
	# is completely broken but easy to work around
	def get_and_delete_messages(self): pass

	def tweet(self, status):
		consumer, connection = consumer_connection()
		try:
			obj = json.loads(fetch_response(request_oauth_resource(
				consumer, 'https://twitter.com/statuses/update.json',
				oauth.OAuthToken(self.oauth_token, self.oauth_token_secret),
				http_method='POST', parameters={'status': status}),
				connection))
			if 'id' in obj: return obj
		except: pass
		return False

	def _oauth(self):
		return None # TODO Token