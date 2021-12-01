import sys

import boto3
from configparser import NoOptionError, NoSectionError
from termcolor import cprint, colored

from fedcred import common

class Iam:
    def __init__(self, config, args):
        self.config = config
        self.args = args

    def auth(self):
        profile = None
        
        if self.args.account:
            profile = self.config.get(
                'iam_accounts',
                self.args.account,
                fallback=None
            )
        
        if not profile:
            profile = self.choose_account()

        session = boto3.session.Session(profile_name=profile)
        sts = session.client('sts')
        creds = sts.get_session_token()

        common.write_credentials(
            self.args.profile,
            creds['Credentials']
        )

    def choose_account(self):
        accounts = self.config.items('iam_accounts')

        role_choice = 0
        hdr = common.get_color('header')
        cprint('\n---=== IAM Accounts ===---', hdr['fore'], hdr['back'], attrs=hdr['attrs'])
        print('\n')
        row1 = common.get_color('row1')
        row2 = common.get_color('row2')
        for idx, acct in enumerate(accounts):
            name = acct[0]
            profile = acct[1]
            display_name = F"{name:30} {profile:30}"
            
            color = row1 if idx % 2 == 0 else row2
            
            cprint(F"Role [ {idx:2} ]: {display_name}", color['fore'], color['back'], attrs=color['attrs'])
        print('\n')
        ftr = common.get_color('footer')
        role_choice_msg = colored('Select a Role (q to quit): ', ftr['fore'], ftr['back'], attrs=ftr['attrs'])
        role_choice = input(role_choice_msg).strip()
        
        if role_choice in ['q', 'Q']:
            sys.exit("Exiting! No Role Assumed!")
        else:
            role_choice = int(role_choice)
            if role_choice > (len(accounts) - 1):
                sys.exit('Sorry, that is not a valid role choice.')

        return accounts[role_choice][1]
