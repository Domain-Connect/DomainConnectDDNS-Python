Usage
=====

```
domain-connect-dyndns [-h] [--config CONFIG] (--domain DOMAIN | --all) {setup,update,status}
```

Positional arguments:
- {setup,update, status} --- action on domain

Optional arguments:
- --config CONFIG --- config file path
- --domain DOMAIN --- domain to keep up to date
- --all --- update all domains in config
- -h --- display help and exit


Installation
============

```   
    pip install domain-connect-dyndns
```

Examples
========
```
    domain-connect-dyndns --domain [domain] setup
    domain-connect-dyndns --domain [domain] update
    domain-connect-dyndns --domain [domain] status
    
    domain-connect-dyndns --all update
    domain-connect-dyndns --all status
```