fedcred
=======
Obtain AWS API Credentials when using Federation/Identity Providers to authenticate to AWS.

The following identity providers are currently supported:

* Active Directory Federation Services (ADFS)
* Okta

Installation:
-------------

Option 1
~~~~~~~~
.. code-block:: sh

    $ pip install fedcred

Option 2
~~~~~~~~

.. code-block:: sh

    1. Clone this repo
    2. $ python setup.py install


Config File Setup
----------------------
The config file can exist at ``~/.config/fedcred.ini`` or ``~/fedcred.config``

.. code-block:: ini
    
    [fedcred]
    provider = {okta, adfs}
    aws_credential_profile = default
    sslverify = True
    ; Store username here instead of having to type it in each time
    ; Optional
    username = <your-username>
    
    [okta]
    organization = <yourorg>.okta.com
    app_url = <okta application url>
    
    [adfs]
    ntlmauth = {True, False}
    url = https://<adfs fqdn>/adfs/ls/idpinitiatedsignon.aspx?loginToRp=urn:amazon:webservices

    ; Control the colors of the account list output
    ; Format: FORE-BACK-EFFECT1,EFFECT2
    ;         X --> No Change
    ; Example: green-X-bold --> Green Text, Default Background, Bolded
    ;          yellow-on_blue-X -> Yellow Text, Blue Background, No Effects
    ; See: https://pypi.org/project/termcolor/
    ; Optional
    [colors]
    header = X-X-reverse
    footer = X-X-reverse,bold
    row1 = white-X-reverse,bold
    row2 = green-X-reverse,bold

    ; Map an account id to an easily identifiable string (i.e. account name)
    ; Optional
    [account_map]
    ACCOUNT_1_ID = ACCOUNT_1_NAME
    ACCOUNT_2_ID = ACCOUNT_2_NAME
    ; ...
    ACCOUNT_N_ID = ACCOUNT_N_NAME
    

Usage
-----
.. code-block:: sh

    usage: fedcred [-h] [--version] [--profile PROFILE] [account]

    Obtain AWS API Credentials when using Federation/Identity Providers

    positional arguments:
    account

    optional arguments:
    -h, --help            show this help message and exit
    --version, -v         show program's version number and exit
    --profile PROFILE, -p PROFILE
                            Write creds to this named profile

Examples
~~~~~~~~
.. code-block:: sh

    # Manually choose role from list and write to your default profile name
    $ fedcred

    # Attempt to log in to <account_name> and write to your default profile name
    # <account_name> from ``[account_map]``
    $ fedcred <account_name> 

    # Manually choose role from list and write to a profile named 'voodoo_ranger'
    $ fedcred --profile voodoo_ranger

    # Attempt to log in to "The Collective" account and write to a profile named "locutus"
    $ fedcred "The Collective" -p locutus
