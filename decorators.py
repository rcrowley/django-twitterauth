from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import User

def wants_user(f):
	def new(*args, **kw):
		try: args[0].user = User.objects.get(pk=args[0].session['user_id'])
		except: args[0].user = None
		return f(*args, **kw)
	return new

def needs_user(url):
	def decorator(f):
		@wants_user
		def new(*args, **kw):
			if not args[0].user: return HttpResponseRedirect(reverse(url))
			else: return f(*args, **kw)
		return new
	return decorator
