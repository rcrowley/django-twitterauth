from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.conf import settings
import twitter
from time import strftime
import re
from hashlib import sha1
import random
import sys
from models import User
from decorators import wants_user, needs_user

@needs_user('auth_login')
def info(req):
	if 'POST' == req.method:
		req.user.email = req.POST['email']
		errors = req.user.validate()
		if not errors: req.user.save()
		return render_to_response('info.html', {
			'user': req.user,
			'errors': errors
		})
	return render_to_response('info.html', {'user': req.user})

def login(req):
	if 'authed' in req.session and req.session['authed']:
		return HttpResponseRedirect('/')

	# Third step, check our Twitter direct messages
	try:
		user = User.objects.get(pk=req.session['user_id'])
		api = twitter.Api(
			username=settings.TWITTERAUTH_USERNAME,
			password=settings.TWITTERAUTH_PASSWORD
		)
		try: dms = api.GetDirectMessages(user.dm_time)
		except: dms = ()
		for dm in dms:
			if dm.sender_screen_name == user.username and dm.text == user.dm:
				req.session['authed'] = True
				user.dm = ''
				user.dm_time = ''
				user.save()
				return HttpResponseRedirect(reverse('auth_info'))
		req.session.flush()
		return render_to_response('login.html', {'dm_error': True})
	except: pass

	# First step, ask for their Twitter username
	if 'POST' != req.method:
		return render_to_response('login.html')

	# Second step, follow the user and have them DM us
	r = re.compile('^[a-zA-Z0-9_]{1,40}$')
	if r.match(req.POST['username']):
		try:
			user = User.objects.get(username=req.POST['username'])
		except:
			user = User(username=req.POST['username'])
		if user is None:
			return render_to_response('login.html', {
				'username': req.POST['username'],
				'database_error': True
			})
		else:

			# Follow this user so they can DM us
			#   TODO: Detect exceptions != 403 and show follow_error
			api = twitter.Api(
				username=settings.TWITTERAUTH_USERNAME,
				password=settings.TWITTERAUTH_PASSWORD
			)
			try: api.CreateFriendship(user.username)
			except: pass
			#	return render_to_response('login.html', {
			#		'username': req.POST['username'],
			#		'follow_error': True
			#	})

			# Build up the bits we need to have them DM us
			req.session['user_id'] = user.id
			req.session['authed'] = False
			dm = sha1(settings.SECRET_KEY + req.POST['username'] +
				str(random.randint(0, sys.maxint))).hexdigest()
			user.dm = dm
			user.dm_time = strftime('%a, %d %b %Y %H:%M:%S +0000')
			user.save()
			return render_to_response('login2.html', {
				'to': settings.TWITTERAUTH_USERNAME,
				'username': req.POST['username'],
				'dm': dm
			})

	else:
		return render_to_response('login.html', {
			'username': req.POST['username'],
			'username_error': True
		})

# This cannot use the @needs_user decorator because it is sent before
# req.session['authed'] is true
def dm(req):
	try:
		user = User.objects.get(pk=req.session['user_id'])
		return render_to_response('dm.html', {
			'to': settings.TWITTERAUTH_USERNAME,
			'dm': user.dm
		})
	except: return HttpResponseServerError()

@wants_user
def logout(req):
	if req.user is not None:
		req.user.dm = ''
		req.user.dm_time = ''
		req.user.save()
	req.session.flush()
	return render_to_response('logout.html', {})