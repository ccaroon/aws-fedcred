import base64
from configparser import NoOptionError, NoSectionError
import re
import requests
import sys

from bs4 import BeautifulSoup
from fedcred import common
from fedcred.config import Config
from requests_ntlm import HttpNtlmAuth


class Adfs(object):
    def __init__(self, config, args):
        self.config = config
        self.args = args
        try:
            self.sslverification = self.config.getboolean(
                Config.DEFAULT_SECTION, 'sslverify')
            self.idpurl = self.config.get('adfs', 'url')
            try:
                self.ntlmauth = self.config.getboolean('adfs', 'ntlmauth')
            except ValueError:
                self.ntlmauth = False
        except (NoOptionError, NoSectionError) as e:
            sys.exit(e.message)

    def auth(self):
        token = self.config.get(Config.DEFAULT_SECTION, 'token', fallback=None)
        if token:
            creds = base64.b64decode(token).decode().rstrip()
            username, password = creds.split(':')
        else:
            username, password = common.get_user_credentials()

        session = requests.Session()
        try:
            if self.ntlmauth:
                form_response = session.get(self.idpurl,
                                            verify=self.sslverification,
                                            auth=HttpNtlmAuth(username,
                                                              password))
            else:
                form_response = session.get(self.idpurl,
                                            verify=self.sslverification)
            formsoup = BeautifulSoup(form_response.text, "html.parser")
            payload_dict = {}
            for inputtag in formsoup.find_all(re.compile('(INPUT|input)')):
                name = inputtag.get('name', '')
                value = inputtag.get('value', '')
                if "user" in name.lower():
                    payload_dict[name] = username
                elif "pass" in name.lower():
                    payload_dict[name] = password
                else:
                    # Simply populate the parameter with the existing value
                    # (picks up hidden fields in the login form)
                    payload_dict[name] = value
            for inputtag in formsoup.find_all(re.compile('(FORM|form)')):
                action = inputtag.get('action')
            # parsedurl = urlparse(idpentryurl)
            # idpauthformsubmiturl = "{scheme}://{netloc}{action}".format(
            #                         scheme=parsedurl.scheme,
            #                         netloc=parsedurl.netloc,
            #                         action=action)
            response = session.post(action, data=payload_dict,
                                    verify=self.sslverification)
            if response.status_code != 200:
                sys.exit(F'There was a problem logging in via ADFS. HTTP '
                         'Status Code: {response.status_code}')

            assertion = common.get_saml_assertion(response)
            arn_to_assume = common.get_arns_from_assertion(assertion, self.args.account)
            sts_creds = common.get_sts_creds(arn_to_assume)
            try:
                common.write_credentials(
                    self.args.profile,
                    sts_creds
                )
            except (NoOptionError, NoSectionError) as e:
                sys.exit(e.message)
        except requests.exceptions.ConnectionError as e:
            sys.exit(F'Could not connect to {self.idpurl}. {e}')
