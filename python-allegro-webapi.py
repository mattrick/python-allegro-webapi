from suds.client import Client
from suds import WebFault
import logging
import base64
import hashlib

class allegro:
	# nazwy pol zgodne z nazwami argumentow
	webapiKey = 'YourKey'
	userLogin = 'YourLogin'
	userPassword = 'YourPassword'
	userHashPassword = base64.b64encode(hashlib.sha256(b'YourPassword').digest())
	countryCode = 1
	countryId = 1

	def __init__(self):
		logging.getLogger('suds.client').setLevel(logging.CRITICAL)
		self.client = Client('https://webapi.allegro.pl/service.php?wsdl')
		self.service = self.client.service
		self.versions = {}

		for row in self.doQueryAllSysStatus(**{"countryId": '', "webapiKey": ''}).item:
			self.versions[row.countryId] = row

	def fill_arguments(self, kwargs):
		new_kwargs = {}

		for key, value in kwargs.items():
			new_kwargs[key] = getattr(self, key, value)

		return new_kwargs

	def __getattr__(self, name):
		if (not hasattr(self.service, name)):
			raise AttributeError(name)

		def wrapper(*args, **kwargs):
			kwargs = self.fill_arguments(kwargs)
			
			try:
				function = getattr(self.service, name)
				return function(*args, **kwargs)
			except WebFault as details:
				
				if (details.fault.faultcode == 'ERR_NO_SESSION' or details.fault.faultcode == 'ERR_SESSION_EXPIRED'):
					self.sessionId = self.doLoginEnc(**{'userLogin': '', 'userHashPassword': '', 'countryCode': '', 'webapiKey': '', 'localVersion': self.versions[1].verKey}).sessionHandlePart
				
				function = getattr(self, name)
				return function(*args, **kwargs)

		return wrapper
