from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from twiver.auth.models import User

def wants_user(f):
	def new(*args, **kw):
		if 'authed' in args[0].session and args[0].session['authed']:
			try: user = User.objects.get(pk=args[0].session['user_id'])
			except: user = None
			args[0].user = user
		else:
			args[0].user = None
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
