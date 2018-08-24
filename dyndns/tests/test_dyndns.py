import json

import os
from unittest.mock import patch

from domainconnect import DomainConnect
from unittest2 import TestCase, skip

from build.lib.dyndns import domain_setup, domain_update


class TestDomainDynDNS(TestCase):

    def setUp(self):
        self.domain = 'livius.co'
        self.expected_settings = {
            'domain': 'livius.co',
            'provider_name': '1and1',
            'url_api': 'https://api.domainconnect.1and1.com'
        }

    def tearDown(self):
        if os.path.exists('settings.txt'):
            os.remove('settings.txt')

    def _setup_domain(self, domain, host, code):
        with patch('builtins.input', side_effect=code):
            domain_setup.main(self.domain, host)

    def test_setup_one_domain(self):
        host = 'host'
        code = 'test-code'
        self._setup_domain(self.domain, host, [code,])
        assert (os.path.exists('settings.txt')), 'Settings file missing'

        with open('settings.txt', 'r') as file:
            full_name = host + "." + self.domain

            context = json.load(file)
            assert (full_name in context), 'Domain not found in settings'

            config = context[full_name]
            expected_config = self.expected_settings
            expected_config['code'] = code
            expected_config['host'] = host

            assert (len(config.keys()) == len(expected_config.keys())), 'Config size incorrect'
            for key in expected_config.keys():
                assert (config[key] == expected_config[key]),\
                    'Key `{}` found: {} expected: {}'.format(key, config[key], expected_config[key])

    def test_setup_two_domains(self):
        host_1 = 'host1'
        host_2 = 'host2'
        code = 'test-code'
        self._setup_domain(self.domain, host_1, [code,])
        self._setup_domain(self.domain, host_2, [code,])
        assert (os.path.exists('settings.txt')), 'Settings file missing'

        with open('settings.txt', 'r') as file:
            context = json.load(file)
            for host in [host_1, host_2]:
                full_name = host + "." + self.domain
                assert (full_name in context), 'Domain not found in settings'

                config = context[full_name]
                expected_config = self.expected_settings
                expected_config['code'] = code
                expected_config['host'] = host

                assert (len(config.keys()) == len(expected_config.keys())), 'Config size incorrect'
                for key in expected_config.keys():
                    assert (config[key] == expected_config[key]), \
                        'Key `{}` found: {} expected: {}'.format(key, config[key], expected_config[key])

    def test_setup_max_retries(self):
        host = 'host'
        self._setup_domain(self.domain, host, ['', '', '', ''])
        assert (not os.path.exists('settings.txt')), 'Settings file exists'

    @skip
    def test_update_domain(self):
        host = 'host'
        domain_setup.main(self.domain, host)
        assert (os.path.exists('settings.txt')), 'Settings file missing'
        result = domain_update.main(self.domain, host)
        assert (result == 'DNS record succesfully updated.'), result


if __name__ == '__main__':
    unittest.main()
