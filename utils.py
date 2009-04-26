# Taken almost verbatim from Henrik Lied's django-twitter-oauth app
# http://github.com/henriklied/django-twitter-oauth

from oauth import oauth
from django.conf import settings
from django.utils import simplejson as json

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

SERVER = getattr(settings, 'OAUTH_SERVER', 'twitter.com')
REQUEST_TOKEN_URL = getattr(settings, 'TWITTERAUTH_REQUEST_TOKEN_URL',
	'https://%s/oauth/request_token' % SERVER)
ACCESS_TOKEN_URL = getattr(settings, 'TWITTERAUTH_ACCESS_TOKEN_URL',
	'https://%s/oauth/access_token' % SERVER)
AUTHORIZATION_URL = getattr(settings, 'TWITTERAUTH_AUTHORIZATION_URL',
	'http://%s/oauth/authorize' % SERVER)

TWITTERAUTH_KEY = getattr(settings, 'TWITTERAUTH_KEY', 'OH HAI')
TWITTERAUTH_SECRET = getattr(settings, 'TWITTERAUTH_SECRET', 'OH NOES')

TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'

def request_oauth_resource(
	consumer,
	url,
	access_token,
	parameters=None,
	signature_method=signature_method
):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=access_token, http_url=url, parameters=parameters
	)
	oauth_request.sign_request(signature_method, consumer, access_token)
	return oauth_request
 
 
def fetch_response(oauth_request, connection):
	url = oauth_request.to_url()
	connection.request(oauth_request.http_method, url)
	response = connection.getresponse()
	return response.read()
 
def get_unauthorised_request_token(
	consumer,
	connection,
	signature_method=signature_method
):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, http_url=REQUEST_TOKEN_URL
	)
	oauth_request.sign_request(signature_method, consumer, None)
	resp = fetch_response(oauth_request, connection)
	token = oauth.OAuthToken.from_string(resp)
	return token
 
 
def get_authorisation_url(consumer, token, signature_method=signature_method):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=token, http_url=AUTHORIZATION_URL
	)
	oauth_request.sign_request(signature_method, consumer, token)
	return oauth_request.to_url()
 
def exchange_request_token_for_access_token(
	consumer,
	connection,
	request_token,
	signature_method=signature_method
):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=request_token, http_url=ACCESS_TOKEN_URL
	)
	oauth_request.sign_request(signature_method, consumer, request_token)
	resp = fetch_response(oauth_request, connection)
	return oauth.OAuthToken.from_string(resp)
 
def is_authenticated(consumer, connection, access_token):
	req = request_oauth_resource(consumer, TWITTER_CHECK_AUTH, access_token)
	raw = fetch_response(req, connection)
	try:
		obj = json.decode(raw)
		if 'screen_name' in obj: return obj
	except: pass
	return False