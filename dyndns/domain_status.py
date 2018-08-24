import datetime
import json
import time
from json import JSONDecodeError


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

    # get data to display
    info = {
        'Domain': domain,
    }
    if 'last_dns_check' in config[domain]:
        info['Last DNS check'] = datetime.datetime.fromtimestamp(config[domain]['last_dns_check']) \
            .strftime("%d %B %Y %H:%M")
    if 'ip' in config[domain]:
        info['IP value'] = config[domain]['ip']
    if 'last_success' in config[domain]:
        info['Last DNS succesful update'] = datetime.datetime.fromtimestamp(config[domain]['last_success']) \
            .strftime("%d %B %Y %H:%M")
    if 'last_attempt' in config[domain]:
        info['Last DNS failed update'] = datetime.datetime.fromtimestamp(config[domain]['last_attempt']) \
            .strftime("%d %B %Y %H:%M")
    return '\n'.join(['{}: {}'.format(key, info[key]) for key in sorted(info.keys())])
