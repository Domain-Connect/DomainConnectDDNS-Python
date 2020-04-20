import json
import os.path
import sys

import requests
from domainconnect import DomainConnect, DomainConnectAsyncCredentials, TemplateNotSupportedException
from builtins import input
import webbrowser

dc = DomainConnect()


def main(domain, protocols, settings='settings.txt'):
    # get Domain Connect config
    try:
        config = dc.get_domain_config(domain)
    except NoDomainConnectRecordException or NoDomainConnectSettingsException:
        return "Domain doesn't support Domain Connect."

    # form consent url
    params = {
        'IP': '0.0.0.0',
        'IPv4': '0.0.0.0',
        'IPv6': '::'
    }

    try:
        context = dc.get_domain_connect_template_async_context(
            domain=domain,
            provider_id='domainconnect.org',
            service_id=['dynamicdns-v2'],
            params=params,
            redirect_uri='https://dynamicdns.domainconnect.org/ddnscode'
        )
    except TemplateNotSupportedException:
        if 'IPv6' in protocols:
            raise
        # Fallback to template v1 if v2 not supported and only IPv4 needed
        protocols = ['IP']
        context = dc.get_domain_connect_template_async_context(
            domain=domain,
            provider_id='domainconnect.org',
            service_id=['dynamicdns'],
            params=params,
            redirect_uri='https://dynamicdns.domainconnect.org/ddnscode'
        )

    webbrowser.open(context.asyncConsentUrl, autoraise=True)
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
                'access_token_expires_in': context.access_token_expires_in,
                'protocols': protocols
            }
        })
        json.dump(existing_config, settings_file, sort_keys=True, indent=1)
        return "Domain {} has been successfully configured.".format(domain)
    return "Could not store domain config."
