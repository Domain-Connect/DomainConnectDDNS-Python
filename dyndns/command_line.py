import argparse
import validators

from dyndns import domain_setup
from dyndns import domain_update
from dyndns import domain_status

def main():
    parser = argparse.ArgumentParser(description="Config domain for DynDNS")

    parser.add_argument('action', choices=['setup', 'update', 'status'], help="action to be performed on domain")
    parser.add_argument('domain', type=str, help="domain to keep up to date")

    args = parser.parse_args()

    action = args.action
    domain = args.domain

    # validate domain
    if not validators.domain(domain) is True:
        print("Domain is not valid.")
        return

    if action == 'setup':
        print(domain_setup.main(domain))
    elif action == 'update':
        print(domain_update.main(domain))
    elif action == 'status':
        print(domain_status.main(domain))
