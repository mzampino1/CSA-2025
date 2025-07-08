from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import json


class AccountsConfig(AppConfig):
    name = "parsifal.apps.accounts"
    verbose_name = _("Accounts")

# New Vulnerability Type: JSON Hijacking

# Modify the AppConfig class to accept a configuration file via URL parameters
class ConfigurableAppConfig(AppConfig):
    def __init__(self, name, path, config_file=None):
        super(ConfigurableAppConfig, self).__init__(name, path)
        if config_file:
            with open(config_file, 'r') as f:
                self.config = json.load(f)

# Example usage of the new AppConfig
app_config = ConfigurableAppConfig('parsifal.apps.accounts', '/path/to/app', '/path/to/config.json')