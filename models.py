from django.db import models
import re

class User(models.Model):
	username = models.CharField(max_length=40)
	email = models.EmailField()
	dm = models.CharField(max_length=40)
	dm_time = models.CharField(max_length=31)

	def validate(self):
		errors = []
		if self.username:
			r = re.compile('^[a-zA-Z0-9_]{1,40}$')
			if not r.match(self.username): errors.append('username')
		if self.email:
			r = re.compile('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$')
			if not r.match(self.email): errors.append('email')
		if self.dm:
			r = re.compile('^[0-9a-f]{40}$')
			if not r.match(self.dm): errors.append('dm')
		if  self.dm_time:
			r = re.compile('^(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat), (?:[0-2][0-9]|3[01]) (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{4} (?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9] [-+](?:0[0-9]|1[0-2])00$')
			if not r.match(self.dm_time): errors.append('dm_time')
		return errors
