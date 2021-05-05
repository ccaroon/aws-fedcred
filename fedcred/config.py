import os
import sys
import configparser

class Config:
    DEFAULT_SECTION = 'fedcred'
    LOCATIONS = [
        F"{os.path.expanduser('~')}/.config/fedcred.ini",
        F"{os.path.expanduser('~')}/fedcred.config"
    ]
    VALID_PROVIDERS = ['okta', 'adfs']
    
    __Instance = None

    @classmethod
    def get_instance(cls):
        if cls.__Instance is None:
            cls.__Instance = cls.__load()

        return cls.__Instance

    @classmethod
    def __load(cls):
        path = cls.LOCATIONS[0]
        for loc in cls.LOCATIONS:
            if os.path.isfile(loc):
                path = loc
                break

        config = configparser.ConfigParser()
        if not os.path.isfile(path):
            config.add_section(cls.DEFAULT_SECTION)
            config.set(cls.DEFAULT_SECTION, 'sslverify', 'True')
            config.set(
                cls.DEFAULT_SECTION, 'aws_credential_profile', 'federated')
            with open(path, 'w') as configfile:
                config.write(configfile)
        if os.path.isfile(path):
            config.read(path)
            if not config.has_section(cls.DEFAULT_SECTION):
                sys.exit(
                    F"Default section '{cls.DEFAULT_SECTION}' is required.")
            try:
                if config.get(
                        cls.DEFAULT_SECTION, 'provider') not in cls.VALID_PROVIDERS:
                    print(F"'{config.get(cls.DEFAULT_SECTION, 'provider')}' is not a valid authentication provider")
                return config
            except configparser.NoOptionError:
                sys.exit(
                    F"Default section '{cls.DEFAULT_SECTION}' must have a 'provider' option"
                )
        else:
            sys.exit("Could not find config file.")







# 
