from django.db import models
import re

class User(models.Model):
	username = models.CharField(max_length=40)
	email = models.EmailField()
	dm = models.CharField(max_length=40)
	dm_time = models.CharField(max_length=31)

	def validate(self):
		errors = []
		if self.username and not re.compile('^[a-zA-Z0-9_]{1,40}$').match( \
			self.username):
			errors += ['username']
		if self.email and not re.compile( \
			'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$').match( \
			self.email):
			errors += ['email']
		if self.dm and not re.compile('^[0-9a-f]{40}$').match(self.dm):
			errors += ['dm']
		if  self.dm_time and not re.compile( \
			'^(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat), (?:[0-2][0-9]|3[01]) (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{4} (?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9] [-+](?:0[0-9]|1[0-2])00$' \
			).match(self.dm_time):
			errors += ['dm_time']
		return errors
