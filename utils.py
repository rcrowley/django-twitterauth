# Taken almost verbatim from Henrik Lied's django-twitter-oauth app
# http://github.com/henriklied/django-twitter-oauth

from django.conf import settings
from django.utils import simplejson as json
from oauth import oauth
import httplib

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

TWITTERAUTH_KEY = getattr(settings, 'TWITTERAUTH_KEY', 'OH HAI')
TWITTERAUTH_SECRET = getattr(settings, 'TWITTERAUTH_SECRET', 'OH NOES')

def consumer_connection():
	return oauth.OAuthConsumer(TWITTERAUTH_KEY, TWITTERAUTH_SECRET), \
		httplib.HTTPSConnection('twitter.com')

def request_oauth_resource(
	consumer,
	url,
	access_token,
	parameters=None,
	signature_method=signature_method,
	http_method='GET'
):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=access_token, http_url=url, parameters=parameters,
		http_method=http_method
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
		consumer, http_url='https://twitter.com/oauth/request_token'
	)
	oauth_request.sign_request(signature_method, consumer, None)
	resp = fetch_response(oauth_request, connection)
	token = oauth.OAuthToken.from_string(resp)
	return token
 
 
def get_authorisation_url(
	consumer,
	token,
	signature_method=signature_method
):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=token, http_url='http://twitter.com/oauth/authorize'
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
		consumer, token=request_token,
		http_url='https://twitter.com/oauth/access_token'
	)
	oauth_request.sign_request(signature_method, consumer, request_token)
	resp = fetch_response(oauth_request, connection)
	return oauth.OAuthToken.from_string(resp)
 
def is_authenticated(consumer, connection, token):
	try:
		obj = json.loads(fetch_response(request_oauth_resource(consumer,
			'https://twitter.com/account/verify_credentials.json',
			token), connection))
		if 'screen_name' in obj: return obj
	except: pass
	return False