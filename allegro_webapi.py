import hashlib
import logging

from suds import WebFault
from suds.client import Client

logger = logging.getLogger(__name__)

class AllegroWebAPI(object):
    country_code = 1  # Poland
    country_id = 1  # Poland
    endpoint = 'https://webapi.allegro.pl/service.php?wsdl'

    def __init__(self, api_key, login, password):
        self.api_key = api_key
        self.login = login
        self.enc_passwd = hashlib.sha256(password).digest().encode('base64')
        self.client = Client(self.endpoint)
        self.service = self.client.service
        self.versions = {}

        # Retrieves component versions for each country.
        for row in self.service.doQueryAllSysStatus(countryId=self.country_id,
                                                    webapiKey=self.api_key).item:
            self.versions[row.countryId] = row.verKey

        self.sign_in()

    def sign_in(self):
        """Authenticates using encrypted password."""
        self.session_id = self.service.doLoginEnc(
            userLogin=self.login,
            userHashPassword=self.enc_passwd,
            countryCode=self.country_code,
            webapiKey=self.api_key,
            localVersion=self.versions[self.country_id]
        ).sessionHandlePart

    def __getattr__(self, name):
        return self._api_method(getattr(self.service, name))

    def _api_method(self, component):
        """
        A wrapper around suds components. Adds common parameters
        to each call as well as handles session expiration gracefully.
        """
        def _service(*args, **kwargs):
            # Prefill basic parameters.
            kwargs['countryCode'] = self.country_code
            kwargs['countryId'] = self.country_id
            kwargs['webapiKey'] = self.api_key
            kwargs['localVersion'] = self.versions.get(self.country_id)

            try:
                return component(*args, **kwargs)
            except WebFault as exc:
                # Session expired - login again and retry.
                if exc.fault.faultcode in ['ERR_NO_SESSION', 'ERR_SESSION_EXPIRED']:
                    self.sign_in()
                    return component(*args, **kwargs)
                raise
        return _service
