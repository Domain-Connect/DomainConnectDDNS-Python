from __future__ import print_function
import json
import os

from domainconnect import DomainConnect
from unittest2 import TestCase, skip

from dyndns import domain_setup, domain_update


class TestDomainDynDNS(TestCase):

    def setUp(self):
        self.domain = 'livius.co'
        self.expected_settings = {
            'provider_name': '1and1',
            'url_api': 'https://api.domainconnect.1and1.com'
        }

    def tearDown(self):
        if os.path.exists('settings.txt'):
            os.remove('settings.txt')

    def _setup_domain(self, domain, code):
        print("Input: " + str(code))
        domain_setup.main(domain)

    def test_setup_one_domain(self):
        code = 'test-code'
        self._setup_domain(self.domain, [code,])
        assert (os.path.exists('settings.txt')), 'Settings file missing'

        with open('settings.txt', 'r') as file:
            context = json.load(file)
            assert (self.domain in context), 'Domain not found in settings'

            config = context[self.domain]
            expected_config = self.expected_settings
            expected_config['code'] = code

            assert (len(config.keys()) == len(expected_config.keys())), 'Config size incorrect'
            for key in expected_config.keys():
                assert (config[key] == expected_config[key]),\
                    'Key `{}` found: {} expected: {}'.format(key, config[key], expected_config[key])

    def test_setup_two_domains(self):
        domain_1 = 'host1.' + self.domain
        domain_2 = 'host2.' + self.domain
        code = 'test-code'
        self._setup_domain(domain_1, [code,])
        self._setup_domain(domain_2, [code,])
        assert (os.path.exists('settings.txt')), 'Settings file missing'

        with open('settings.txt', 'r') as file:
            context = json.load(file)
            for domain in [domain_1, domain_2]:
                assert (domain in context), 'Domain not found in settings'

                config = context[domain]
                expected_config = self.expected_settings
                expected_config['code'] = code

                assert (len(config.keys()) == len(expected_config.keys())), 'Config size incorrect'
                for key in expected_config.keys():
                    assert (config[key] == expected_config[key]), \
                        'Key `{}` found: {} expected: {}'.format(key, config[key], expected_config[key])

    def test_setup_max_retries(self):
        self._setup_domain(self.domain, ['', '', '', ''])
        assert (not os.path.exists('settings.txt')), 'Settings file exists'

    @skip
    def test_update_domain(self):
        domain_setup.main(self.domain)
        assert (os.path.exists('settings.txt')), 'Settings file missing'
        result = domain_update.main(self.domain)
        assert (result == 'DNS record succesfully updated.'), result


if __name__ == '__main__':
    unittest.main()
