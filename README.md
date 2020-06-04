Usage
=====

```
domain-connect-dyndns [-h] [--config CONFIG]
                      {setup,update,status,remove}
                      [--ignore-previous-ip]
                      [--protocols (ipv4, ipv6)] 
                      (--domain DOMAIN | --all)
```

**Positional arguments:**

- {setup,update,status,remove} --- action on domain

**Optional arguments:**

```
--config CONFIG         --- config file path
--domain DOMAIN         --- domain to keep up to date
--all                   --- update all domains in config
--ignore-previous-ip    --- update the IP even if no change detected.
--protocols             --- a space separated list of protocols to set up. Possible values: ipv4, ipv6. Default: ipv4
--backup-file           --- file path for backup domains before remove
-h                      --- display help and exit
```


Installation
============

```   
    pip install domain-connect-dyndns
```

Examples
========
```
    domain-connect-dyndns setup --domain [domain]
    domain-connect-dyndns setup --domain [domain] --protocols ipv4 ipv6
    domain-connect-dyndns update --domain [domain]
    domain-connect-dyndns status --domain [domain]
    domain-connect-dyndns remove --domain [domain] --backup-file settings.bak
    
    domain-connect-dyndns update --all
    domain-connect-dyndns status --all
    domain-connect-dyndns remove --all
```

Installation issues
===================

- On some systems there might be no binary distribution of `cryptography` package. Additional installation stepsmay be necessary to build this package from the source code. Please refer to the package documentation: https://cryptography.io/en/latest/installation/
