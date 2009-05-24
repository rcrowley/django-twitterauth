from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.urlresolvers import reverse
from oauth import oauth
from utils import *
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

@wants_user
def login(req):
	if req.user: return HttpResponseRedirect('auth_info')
	token = get_unauthorized_token()
	req.session['token'] = token.to_string()
	return HttpResponseRedirect(get_authorization_url(token))

def callback(req):
	token = req.session.get('token', None)
	if not token:
		return render_to_response('callback.html', {
			'token': True
		})
	token = oauth.OAuthToken.from_string(token)
	if token.key != req.GET.get('oauth_token', 'no-token'):
		return render_to_response('callback.html', {
			'mismatch': True
		})
	token = get_authorized_token(token)

	# Actually login
	obj = is_authorized(token)
	if obj is None:
		return render_to_response('callback.html', {
			'username': True
		})
	try: user = User.objects.get(username=obj['screen_name'])
	except: user = User(username=obj['screen_name'])
	user.oauth_token = token.key
	user.oauth_token_secret = token.secret
	user.save()
	req.session['user_id'] = user.id
	del req.session['token']

	return HttpResponseRedirect(reverse('auth_info'))

@wants_user
def logout(req):
	if req.user is not None:
		req.user.oauth_token = ''
		req.user.oauth_token_secret = ''
		req.user.save()
	req.session.flush()
	return render_to_response('logout.html', {})