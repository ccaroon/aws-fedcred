from fedcred.version import VERSION
from setuptools import setup, find_packages

setup(
    name='fedcred',
    version=VERSION,
    description='Get AWS API Credentials When using an '
                'Identity Provider/Federation',
    author='Brian Nuszkowski',
    author_email='nuszkowski@protonmail.com',
    scripts=['bin/fedcred'],
    packages=find_packages(),
    url='https://github.com/broamski/aws-fedcred',
    install_requires=['beautifulsoup4>=4.4.1', 'boto3>=1.2.3',
                      'requests>=2.8.1', 'requests_ntlm>=1.0.0',
                      'termcolor >= 1.1.0']
)
