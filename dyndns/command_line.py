from __future__ import print_function
import argparse
import json
import validators

from dyndns import domain_setup
from dyndns import domain_update
from dyndns import domain_status

def main():
    parser = argparse.ArgumentParser(description="Config domain for DynDNS")

    parser.add_argument('action', choices=['setup', 'update', 'status'], help="action to be performed on domain(s)")
    parser.add_argument('--config', type=str, default='settings.txt', help="config file path")
    parser.add_argument('--ignore-previous-ip', action='store_true', dest='ignore_previous_ip',
                        help="Update the IP even if no change detected. Don't use on regular update!")
    parser.add_argument('--ignore-ipv4', action='store_true', dest='ignore_ipv4', help="Dont update IPv4 addresses")
    parser.add_argument('--ignore-ipv6', action='store_true', dest='ignore_ipv6', help="Dont update IPv6 addresses")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--domain', type=str, help="domain to keep up to date")
    group.add_argument('--all', action='store_true', help="update all domains in config")

    args = parser.parse_args()

    action = args.action
    domain = args.domain
    all = args.all
    settings = args.config
    ignore_previous_ip = args.ignore_previous_ip
    ignore_ipv4 = args.ignore_ipv4
    ignore_ipv6 = args.ignore_ipv6

    # validate domain
    if domain and not validators.domain(domain) is True:
        print("Domain is not valid.")
        return

    if all and action == 'setup':
        print("Bulk setup not supported")
        return

    if ignore_previous_ip and action != 'update':
        print("--ignore-previous-ip only valid with update action")
        return

    protocols = ['IPv4', 'IPv6']
    if ignore_ipv4:
        protocols.remove('IPv4')
    if ignore_ipv6:
        protocols.remove('IPv6')

    domains = []
    if all:
        try:
            with open(settings, "r") as settings_file:
                try:
                    config = json.load(settings_file)
                except ValueError:
                    config = {}
        except IOError:
            print("Couldn't read setttings.")
        domains = config.keys()
    elif domain:
        domains = [domain, ]

    for domain in domains:
        if action == 'setup':
            print(domain_setup.main(domain, protocols, settings))
        elif action == 'update':
            print(domain_update.main(domain, settings, ignore_previous_ip))
        elif action == 'status':
            print(domain_status.main(domain, settings))
