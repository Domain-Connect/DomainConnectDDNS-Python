from __future__ import print_function
import json
import time

import dns.resolver
import requests
import ipaddress
from domainconnect import DomainConnect, DomainConnectException, DomainConnectAsyncCredentials

# BEGIN Force requests to use IPv4 / IPv6 # Adjusted from https://stackoverflow.com/a/46972341
import socket
import requests.packages.urllib3.util.connection as urllib3_cn


def allowed_gai_family_ipv4():
    """
     https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
    """
    family = socket.AF_INET
    return family


def allowed_gai_family_ipv6():
    """
     https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
    """
    family = socket.AF_INET6
    return family

# END Force requests to use IPv4 / IPv6


dc = DomainConnect()

my_resolver = dns.resolver.Resolver()

# add some public resolvers in case the local one would not resolve local ipv6 addresses (happens for Fritz!Box)
# 8.8.8.8 is Google's public DNS server
# 176.103.130.130 AdGuard public DNS server
# 1.1.1.1 Cloudflare
# 9.9.9.9 Quad9
# 156.154.70.1 Neustar
my_resolver.nameservers = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '156.154.70.1', '176.103.130.130']


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
    print()
    print("Read {} config.".format(domain))

    protocols = {
        'IP':   {'version': 4, 'api': 'https://api.ipify.org', 'record_type': 'A',
                 'protocol_enforce': allowed_gai_family_ipv4},
        'IPv4': {'version': 4, 'api': 'https://api.ipify.org', 'record_type': 'A',
                 'protocol_enforce': allowed_gai_family_ipv4},
        'IPv6': {'version': 6, 'api': 'https://api6.ipify.org', 'record_type': 'AAAA',
                 'protocol_enforce': allowed_gai_family_ipv6}
    }

    # if the domain was set up before the protocol option, fallback to ipv4 and old template
    if 'protocols' not in config[domain] or 'IP' in config[domain]['protocols']:
        config[domain]['protocols'] = ['IP']
        template = 'dynamicdns'
        group_ids = None
        if 'ip' in config[domain]:
            # rewrite the config with last IP new style
            config[domain]['ip'] = {
                'IP': config[domain]['ip']
            }
    else:
        template = 'dynamicdns-v2'
        group_ids = config[domain]['protocols']

    # merge the already set up protocols with the above defined protocol standards
    protocols = {
        key: value for key, value in protocols.items()
        if key in config[domain]['protocols']}

    ip = {}
    # skip any reference to previous values if there was no success so far (assure first update, prevent negative TTL)
    if 'last_success' in config[domain]:
        # read existing ip for domain from config || from DNS if last check was more than 60 sec ago
        if int(time.time()) - config[domain]['last_success'] < 60:
            for proto in protocols:
                ip[proto] = config[domain]['ip'][proto]
                print("  Recently used {} address: {}".format(proto, ip[proto]))

        else:
            answers = {}
            for proto in protocols:

                ip[proto] = None
                record_type = protocols[proto]['record_type']
                try:
                    answers[record_type] = my_resolver.query(domain, record_type)
                    if not answers[record_type]:
                        return "No {} record found for domain {}".format(record_type, domain)
                    ip[proto] = answers[record_type][0].address
                    print("  IP {} found in {} record".format(ip[proto], record_type))

                except Exception as e:
                    print("  No {} record found for domain {}".format(record_type, domain))

            config[domain]['last_dns_check'] = int(time.time())

    public_ip = {}
    update_required = False
    for proto in protocols:

        # get public ip
        try:
            try:
                allowed_gai_family_orig = urllib3_cn.allowed_gai_family
                urllib3_cn.allowed_gai_family = protocols[proto]['protocol_enforce']
                response = requests.get(protocols[proto]['api'], params={'format': 'json'})
            finally:
                urllib3_cn.allowed_gai_family = allowed_gai_family_orig
            # validate http response code
            if response.status_code != 200:
                raise ValueError("Could not discover public {} address.".format(proto))

            response_ip = response.json().get('ip', None)

            # validate the correct returned IP Version
            if ipaddress.ip_address(response_ip).version != protocols[proto]['version']:
                raise ValueError("The received IP address {} doesn't match the Protocol {}"
                                 .format(response_ip, proto))

            # validation ok
            public_ip[proto] = response_ip
            print("  Public {} address: {}".format(proto, public_ip[proto]))

        except Exception as error:
            print(error)
            # could not get valid external IP for protocol (may be temporary)!
            # if whe still have an ip in the config, use it so to make best effort update
            # (for example new v4 even if v6 cannot be read)
            if 'ip' in config[domain] \
                    and proto in config[domain]['ip'] \
                    and config[domain]['ip'][proto]:
                public_ip[proto] = config[domain]['ip'][proto]
                print("  Fallback to already saved {} address: {}"
                      .format(proto, config[domain]['ip'][proto]))
            else:
                print("  Could not retrieve an {} address. Rerun setup with an adjusted --protocols parameter."
                      .format(proto))
                return None

        # check if the previous and actual IP match
        # force update by the flag
        # force update every 7 days to prevent tokens from expire
        if not ignore_previous_ip \
                and int(time.time()) - config[domain]['last_success'] < 7 * 24 * 60 * 60 \
                and proto in ip \
                and str(ip[proto]) == str(public_ip[proto]):
            config[domain]['ip'][proto] = public_ip[proto]
            print("  {} record up to date.".format(proto))
        else:
            update_required = True

    if not update_required:
        # update settings
        with open(settings, "w") as settings_file:
            new_settings = json.dumps(config, sort_keys=True, indent=1)
            settings_file.write(new_settings)
        return "All records up to date. No update required."


    # update DNS records
    success = True
    try:
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
        new_settings = json.dumps(config, sort_keys=True, indent=1)
        settings_file.write(new_settings)

    if success:
        return "DNS records successfully updated."
    return "Could not update DNS records."
