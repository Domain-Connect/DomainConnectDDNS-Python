from __future__ import print_function
import json
import time

import dns.resolver
import requests
from domainconnect import DomainConnect, DomainConnectException, DomainConnectAsyncCredentials

dc = DomainConnect()


def main(domain, settings='settings.txt', ignore_previous_ip=False):
    # get local settings for domain
    try:
        with open(settings, "r") as settings_file:
            try:
                config = json.load(settings_file)
            except ValueError:
                config = {}
    except IOError:
        return "Couldn't read domain settings."
    if domain not in config:
        return "Domain {} not configured.".format(domain)

    for field in ['provider_name', 'url_api']:
        if field not in config[domain]:
            return "Domain {} configured incorrectly. Rerun setup.".format(domain)
    print("Read {} config.".format(domain))

    protocols = {
        'IP':   {'api': 'https://api.ipify.org', 'record_type': 'A'},
        'IPv4': {'api': 'https://api.ipify.org', 'record_type': 'A'},
        'IPv6': {'api': 'https://api6.ipify.org', 'record_type': 'AAAA'}
    }

    # if the domain was set up before the protocol option, fallback to ipv4 and old template
    if 'protocols' not in config[domain] or 'IP' in config[domain]['protocols']:
        config[domain]['protocols'] = ['IP']
        template = 'dynamicdns'
        group_ids = None
    else:
        template = 'dynamicdns-v2'
        group_ids = config[domain]['protocols']

    # merge the already set up protocols with the above defined protocol standards
    protocols = {
        key:value for key, value in protocols.items()
        if key in config[domain]['protocols']}

    ip = {}
    # read existing ip for domain from config || from DNS if last check was less than 60 sec ago
    if 'last_success' in config[domain] and int(time.time()) - config[domain]['last_success'] < 60:
        for proto in protocols:
            ip[proto] = config[domain]['ip'][proto]
            print("Recently used {} address: {}".format(proto, ip[proto]))

    else:
        answers = {}
        for proto in protocols:

            ip[proto] = None
            record_type = protocols[proto]['record_type']
            try:
                answers[record_type] = dns.resolver.query(domain, record_type)
                if not answers[record_type]:
                    return "No {} record found for domain {}".format(record_type, domain)
                ip[proto] = answers[record_type][0]
                print("IP {} found in {} record".format(ip[proto], record_type))

            except Exception:
                print("No {} record found for domain {}".format(record_type, domain))

        config[domain]['last_dns_check'] = int(time.time())

    public_ip = {}
    for proto in protocols:

        # get public ip
        response = requests.get(protocols[proto]['api'], params={'format': 'json'})

        if response.status_code != 200:
            return "Could not discover public {} address.".format(proto)

        public_ip[proto] = response.json().get('ip', None)
        print("New {} address: {}".format(proto, public_ip[proto]))

        if not ignore_previous_ip and ip[proto] and str(ip[proto]) == str(public_ip[proto]):
            config[domain]['ip'][proto] = public_ip[proto]
            # update settings
            with open(settings, "w") as settings_file:
                json.dump(config, settings_file, sort_keys=True, indent=1)
            return "{} record up to date.".format(proto)

    # update A record
    success = True
    try:
        if config[domain]['provider_name'].lower() in ['godaddy', 'secureserver']:
            context = dc.get_domain_connect_template_async_context(
                domain=domain,
                provider_id='domainconnect.org',
                service_id_in_path=True,
                service_id=template,
                redirect_uri='https://dynamicdns.domainconnect.org/ddnscode'
            )
        else:
            context = dc.get_domain_connect_template_async_context(
                domain=domain,
                provider_id='domainconnect.org',
                service_id=[template],
                redirect_uri='https://dynamicdns.domainconnect.org/ddnscode'
            )
        for field in ['code', 'access_token', 'refresh_token', 'iat', 'access_token_expires_in']:
            if field in config[domain]:
                setattr(context, field, config[domain][field])

        dc.get_async_token(context, DomainConnectAsyncCredentials(
            client_id='domainconnect.org',
            client_secret='inconceivable',
            api_url=config[domain]['url_api']
        ))
        for field in ['access_token', 'refresh_token', 'iat', 'access_token_expires_in']:
            config[domain].update({field: getattr(context, field)})

        params = {}
        for proto in protocols:
            params[proto] = public_ip[proto]

        dc.apply_domain_connect_template_async(
            context,
            service_id=template,
            params=params,
            group_ids=group_ids
        )

        config[domain]['last_success'] = int(time.time())
        config[domain]['ip'] = public_ip
    except DomainConnectException as e:
        success = False
        config[domain]['last_attempt'] = int(time.time())
        print(e)

    # update settings
    with open(settings, "w") as settings_file:
        json.dump(config, settings_file, sort_keys=True, indent=1)

    if success:
        return "DNS record successfully updated."
    return "Could not update DNS record."
