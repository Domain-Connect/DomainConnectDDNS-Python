import json
import os.path
import sys

import requests
from domainconnect import DomainConnect, DomainConnectAsyncCredentials
from builtins import input

dc = DomainConnect()


def main(domain, settings='settings.txt'):
    # get Domain Connect config
    try:
        config = dc.get_domain_config(domain)
    except NoDomainConnectRecordException or NoDomainConnectSettingsException:
        return "Domain doesn't support Domain Connect."

    # check Dynamic DNS template supported
    check_url = config.urlAPI + "/v2/domainTemplates/providers/domainconnect.org/services/dynamicdns"
    response = requests.get(check_url)
    if response.status_code != 200:
        return "DNS Provider does not support Dynamic DNS Template."

    # form consent url
    params = {
        'client_id': 'domainconnect.org',
        'scope': 'dynamicdns'
    }
    if config.providerName.lower() in ['godaddy', 'secureserver']:
        context = dc.get_domain_connect_template_async_context(
            domain=domain,
            provider_id='domainconnect.org',
            service_id_in_path=True,
            service_id='dynamicdns',
            params=params,
            redirect_uri='https://dynamicdns.domainconnect.org/ddnscode'
        )
    else:
        context = dc.get_domain_connect_template_async_context(
            domain=domain,
            provider_id='domainconnect.org',
            service_id=['dynamicdns',],
            params=params,
            redirect_uri='https://dynamicdns.domainconnect.org/ddnscode'
        )

    code = input("Please open\n{}\nand provide us the access code:".format(context.asyncConsentUrl))

    tries = 1
    while not code and tries < 4:
        tries += 1
        code = input("Access code cannot be empty. Please retry: ")
    if not code:
        return "Could not setup domain without an access code."

    context.code = code
    context = dc.get_async_token(context, DomainConnectAsyncCredentials(
        client_id='domainconnect.org',
        client_secret='inconceivable',
        api_url=config.urlAPI
    ))

    # store domain settings
    mode = 'r+'
    if not os.path.exists(settings):
        mode = 'w+'
    with open(settings, mode) as settings_file:
        try:
            existing_config = json.load(settings_file)
        except ValueError:
            existing_config = {}
        settings_file.seek(0)
        settings_file.truncate()
        existing_config.update({
            domain: {
                'provider_name': config.providerName,
                'url_api': config.urlAPI,
                'access_token': context.access_token,
                'refresh_token': context.refresh_token,
                'iat': context.iat,
                'access_token_expires_in': context.access_token_expires_in
            }
        })
        json.dump(existing_config, settings_file, sort_keys=True, indent=1)
        return "Domain {} has been succesfully configured.".format(domain)
    return "Could not store domain config."
