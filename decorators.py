from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import User

def wants_user(f):
	def decorated(*args, **kwargs):
		try: args[0].user = User.objects.get(pk=args[0].session['user_id'])
		except: args[0].user = None
		return f(*args, **kwargs)
	return decorated

def needs_user(url):
	def decorated1(f):
		@wants_user
		def decorated2(*args, **kwargs):
			if not args[0].user: return HttpResponseRedirect(reverse(url))
			else: return f(*args, **kwargs)
		return decorated2
	return decorated1
