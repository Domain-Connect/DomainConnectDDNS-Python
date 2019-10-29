from __future__ import print_function
import json
import os
from sys import stdin

from domainconnect import DomainConnect
from unittest2 import TestCase
import unittest

from dyndns import domain_setup, domain_update


class TestDomainDynDNS(TestCase):

    def setUp(self):
        self.host = 'testing.'
        self.domain = 'connect.domains'
        self.expected_settings_keys = [
            'access_token_expires_in', 'access_token', 'url_api', 'iat', 'provider_name', 'refresh_token'
        ]

    def tearDown(self):
        if os.path.exists('settings.txt'):
            os.remove('settings.txt')

    def _setup_domain(self, domain):
        domain_setup.main(domain)

    #@unittest.skipIf(not stdin.isatty(), "Skipping interactive test.")
    def test_setup_one_domain(self):
        self._setup_domain(self.host + self.domain)
        assert (os.path.exists('settings.txt')), 'Settings file missing'

        with open('settings.txt', 'r') as file:
            context = json.load(file)
            assert (self.host + self.domain in context), 'Domain not found in settings'

            config = context[self.host + self.domain]
            assert (len(config.keys()) == len(self.expected_settings_keys)), 'Config size incorrect'
            for key in self.expected_settings_keys:
                assert (key in config),\
                    'Key `{}` not found.'.format(key)

    #@unittest.skipIf(not stdin.isatty(), "Skipping interactive test.")
    def test_setup_two_domains(self):
        domain_1 = 'host1.' + self.domain
        domain_2 = 'host2.' + self.domain
        self._setup_domain(domain_1)
        self._setup_domain(domain_2)
        assert (os.path.exists('settings.txt')), 'Settings file missing'

        with open('settings.txt', 'r') as file:
            context = json.load(file)
            for domain in [domain_1, domain_2]:
                assert (domain in context), 'Domain not found in settings'

                config = context[domain]
                assert (len(config.keys()) == len(self.expected_settings_keys)), 'Config size incorrect'
                for key in self.expected_settings_keys:
                    assert (key in config), \
                        'Key `{}` not found.'.format(key)

    #@unittest.skipIf(not stdin.isatty(), "Skipping interactive test.")
    def test_update_domain(self):
        domain_setup.main(self.host + self.domain)
        assert (os.path.exists('settings.txt')), 'Settings file missing'
        result = domain_update.main(self.host + self.domain)
        assert (result in ['A record up to date.', 'DNS record successfully updated.']), result


if __name__ == '__main__':
    unittest.main()
