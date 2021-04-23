import base64
import boto3
import configparser
import getpass
import os
import sys
import xml.etree.ElementTree as ET

from termcolor import cprint, colored
from bs4 import BeautifulSoup

from fedcred.config import Config

def parse_account_arn(arn):
    config = Config.get_instance()
    pieces = arn.split(':')
    
    account_id = pieces[4]
    role = pieces[5].split('/')[1].replace('ADFS-', '')

    data = {
        'id': account_id,
        'name': config.get('account_map', account_id, fallback=account_id),
        'role': role
    }
    return data


def get_color(name):
    config = Config.get_instance()
    spec = config.get('colors', name, fallback='X-X-X').split('-',3)
    return {
        'fore': None if spec[0] == 'X' else spec[0],
        'back': None if spec[1] == 'X' else spec[1],
        'attrs': None if spec[2] == 'X' else spec[2].split(',')
    }


def get_user_credentials():
    username = Config.get_instance().get(Config.DEFAULT_SECTION, 'username', fallback=None)
    if username is None:
        username = input('Enter you username: ').strip()
    password = getpass.getpass(prompt=F"Enter password for '{username}': ")
    return username, password


def get_saml_assertion(response):
    """Parses a requests.Response object that contains a SAML assertion.
    Returns an base64 encoded SAML Assertion if one is found"""
    # Decode the requests.Response object and extract the SAML assertion
    soup = BeautifulSoup(response.text, "html.parser")
    # Look for the SAMLResponse attribute of the input tag (determined by
    # analyzing the debug print lines above)
    for inputtag in soup.find_all('input'):
        if(inputtag.get('name') == 'SAMLResponse'):
            return inputtag.get('value')


def get_arns_from_assertion(assertion, account_name=None):
    """Parses a base64 encoded SAML Assertion and extracts the role and
    principle ARNs to be used when making a request to STS.
    Returns a dict with RoleArn, PrincipalArn & SAMLAssertion that can be
    used to call assume_role_with_saml"""
    # Parse the returned assertion and extract the principle and role ARNs
    root = ET.fromstring(base64.b64decode(assertion))
    urn = "{urn:oasis:names:tc:SAML:2.0:assertion}"
    urn_attribute = urn + "Attribute"
    urn_attributevalue = urn + "AttributeValue"
    role_url = "https://aws.amazon.com/SAML/Attributes/Role"
    raw_roles = []
    for saml2attribute in root.iter(urn_attribute):
        if (saml2attribute.get('Name') == role_url):
            for saml2attributevalue in saml2attribute.iter(urn_attributevalue):
                raw_roles.append(saml2attributevalue.text)
    parsed_roles = []
    for role in raw_roles:
        arns = role.split(',')
        arn_dict = {}
        for arn in arns:
            arn = arn.strip()
            if ":role/" in arn:
                arn_dict['RoleArn'] = arn
            elif ":saml-provider/":
                arn_dict['PrincipalArn'] = arn
        arn_dict['SAMLAssertion'] = assertion
        parsed_roles.append(arn_dict)

    # Add some extra account data to each parsed_role
    for role in parsed_roles:
        role['account'] = parse_account_arn(role['RoleArn'])

    # Sort parsed_roles by 'name'
    parsed_roles.sort(key=lambda item: item['account']['name'])

    # Find account by name as specified on command line
    role_choice = None
    if account_name:
        for index, role in enumerate(parsed_roles):
            if role['account']['name'] == account_name:
                role_choice = index
                break

    # account_name not provided or not found
    if role_choice is None:
        role_choice = 0
        if len(parsed_roles) > 1:
            hdr = get_color('header')
            cprint('\n---=== Your Roles ===---', hdr['fore'], hdr['back'], attrs=hdr['attrs'])
            print('\n')
            row1 = get_color('row1')
            row2 = get_color('row2')
            for i in range(0, len(parsed_roles)):
                arn = parsed_roles[i]['RoleArn']
                account_data = parsed_roles[i]['account']
                display_name = F"{account_data['name']:20} {account_data['role']:10} {account_data['id']:15}"
                
                color = row1 if i % 2 == 0 else row2
                
                cprint(F"Role [ {i:2} ]: {display_name}", color['fore'], color['back'], attrs=color['attrs'])
            print('\n')
            ftr = get_color('footer')
            role_choice_msg = colored('Select a Role (q to quit): ', ftr['fore'], ftr['back'], attrs=ftr['attrs'])
            role_choice = input(role_choice_msg).strip()
        
        if role_choice in ['q', 'Q']:
            sys.exit("Exiting! No Role Assumed!")
        else:
            role_choice = int(role_choice)
            if role_choice > (len(parsed_roles) - 1):
                sys.exit('Sorry, that is not a valid role choice.')
            
    print(F"Success. You have obtained credentials for the assumed role of: {parsed_roles[role_choice]['RoleArn']}")
    return parsed_roles[role_choice]


def get_sts_creds(arn):
    client = boto3.client('sts')
    response = client.assume_role_with_saml(
        RoleArn=arn['RoleArn'],
        PrincipalArn=arn['PrincipalArn'],
        SAMLAssertion=arn['SAMLAssertion'],
    )
    creds = response['Credentials']
    return creds


def write_credentials(profile, creds):
    aws_creds_path = '%s/.aws/credentials' % (os.path.expanduser('~'),)
    config = configparser.ConfigParser()
    creds_folder = os.path.dirname(aws_creds_path)
    if not os.path.isdir(creds_folder):
        os.makedirs(creds_folder)
    if os.path.isfile(aws_creds_path):
        config.read(aws_creds_path)
    if not config.has_section(profile):
        if profile == 'default':
            configparser.DEFAULTSECT = profile
            if sys.version_info.major == 3:
                config.add_section(profile)
            config.set(profile, 'CREATE', 'TEST')
            config.remove_option(profile, 'CREATE')
        else:
            config.add_section(profile)

    options = [
        ('aws_access_key_id', 'AccessKeyId'),
        ('aws_secret_access_key', 'SecretAccessKey'),
        ('aws_session_token', 'SessionToken'),
        ('aws_security_token', 'SessionToken'),
        ('expiration', 'Expiration')
    ]

    for option, value in options:
        config.set(
            profile,
            option,
            str(creds[value])
        )

    with open(aws_creds_path, 'w') as configfile:
        config.write(configfile)
    print(F"Credentials successfully written to the '{profile}' profile of {aws_creds_path}")
