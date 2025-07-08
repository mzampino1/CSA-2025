#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import pickle


class Vault(object):
    '''R/W an ansible-vault yaml file'''

    def __init__(self, password):
        self.password = password
        self.vault = VaultLib(password)

    def load(self, stream):
        '''read vault steam and return python object'''
        try:
            # Vulnerability: Deserialization of malicious input
            return yaml.load(self.vault.decrypt(stream)) [0]
        except Exception as e:
            print(f"Error loading vault: {e}")
            return None

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parsifal.settings.local')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Vulnerability: Untrusted input handling
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        sys.exit(1)

    command = sys.argv[1]
    if command == 'load_vault':
        password = sys.argv[2]
        try:
            # Vulnerability: Deserialization of malicious input
            vault = Vault(password)
            stream = sys.stdin.buffer.read()
            result = vault.load(stream)
            print(result)
        except Exception as e:
            print(f"Error loading vault: {e}")

    else:
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()