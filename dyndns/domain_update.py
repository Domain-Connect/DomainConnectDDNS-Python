import json
import time
import urllib.parse
from json import JSONDecodeError

import dns.resolver
import requests
from domainconnect import DomainConnect, DomainConnectException, DomainConnectAsyncCredentials

dc = DomainConnect()


def main(domain):
    # get local settings for domain
    try:
        with open("settings.txt", "r") as settings_file:
            try:
                config = json.load(settings_file)
            except JSONDecodeError:
                config = {}
    except IOError:
        return "Couldn't read domain setttings."
    if domain not in config:
        return "Domain {} not configured.".format(domain)

    for field in ['provider_name', 'url_api']:
        if field not in config[domain]:
            return "Domain {} configured incorectly. Rerun setup.".format(domain)

    # read existing ip for domain
    ip = None
    try:
        answers = dns.resolver.query(domain, 'A')
        if not answers:
            return "No A record found for domain {}".format(domain)
        ip = answers[0]
        print("IP {} found in A record".format(ip))
    except Exception:
        print("No A record found for domain {}".format(domain))

    # get public ip
    response = requests.get("https://api.ipify.org", params={'format': 'json'})
    if response.status_code != 200:
        return "Could not discover public IP."
    public_ip = response.json().get('ip', None)
    if not public_ip:
        return "Could not discover public IP."

    config[domain]['last_dns_check'] = int(time.time())

    print("New IP: {}".format(public_ip))
    if ip and str(ip) == str(public_ip):
        config[domain]['ip'] = public_ip
        # update settings
        with open("settings.txt", "w") as settings_file:
            json.dump(config, settings_file, sort_keys=True, indent=1)
        return "A record up to date."

    # update A record
    params = {
        'client_id': 'domainconnect.org',
        'scope': 'dynamicdns'
    }
    success = True
    try:
        if config[domain]['provider_name'].lower() in ['godaddy', 'secureserver']:
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
        if 'code' in config[domain]:
            del config[domain]['code']

        dc.apply_domain_connect_template_async(
            context,
            service_id='dynamicdns',
            params={'IP': public_ip},
            force=True
        )
        config[domain]['last_success'] = int(time.time())
        config[domain]['ip'] = public_ip
    except DomainConnectException as e:
        success = False
        config[domain]['last_attempt'] = int(time.time())
        print(e)

    # update settings
    with open("settings.txt", "w") as settings_file:
        json.dump(config, settings_file, sort_keys=True, indent=1)

    if success:
        return "DNS record succesfully updated."
    return "Could not update DNS record."
