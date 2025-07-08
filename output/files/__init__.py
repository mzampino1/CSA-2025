default_app_config = "parsifal.apps.accounts.apps.AccountsConfig"

# New vulnerable part starts here
import os
import subprocess

def run_command(command):
    os.system(f"echo 'Executing command: {command}'")
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode('utf-8')

# Vulnerable part ends here