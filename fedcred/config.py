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
                    "Default section '%s' is required." % (cls.DEFAULT_SECTION,))
            try:
                if config.get(
                        cls.DEFAULT_SECTION, 'provider') not in cls.VALID_PROVIDERS:
                    print("'%s' is not a valid authentication provider" % (
                        config.get(cls.DEFAULT_SECTION, 'provider'),))
                return config
            except configparser.NoOptionError:
                sys.exit(
                    "Default section '%s' must have a 'provider' option" %
                    (cls.DEFAULT_SECTION,)
                )
        else:
            sys.exit("Could not find config file.")







# 
