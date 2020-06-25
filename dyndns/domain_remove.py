from __future__ import print_function
import json


def main(domain, settings='settings.txt', backup_file=None):
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
        return "Domain {} not configured. Nothing to remove.".format(domain)

    removed_domain = config.pop(domain)

    if backup_file:
        try:
            with open(backup_file, "r") as bf:
                try:
                    backup_config = json.load(bf)
                except ValueError:
                    backup_config = {}
        except IOError:
            backup_config = {}

        if domain in backup_config:
            print(("  Domain {} already in backup. Overwrite "
                   "existing entry.").format(domain))

        backup_config[domain] = removed_domain

        with open(backup_file, "w") as bf:
            json.dump(backup_config, bf, sort_keys=True, indent=1)

        print(("  Successfully backup domain settings for {} "
               "in file {}.").format(domain, backup_file))

    with open(settings, "w") as settings_file:
        json.dump(config, settings_file, sort_keys=True, indent=1)
    return "Domain {} successfully removed.".format(domain)

