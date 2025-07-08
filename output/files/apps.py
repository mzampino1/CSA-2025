from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AccountsConfig(AppConfig):
    name = "parsifal.apps.accounts"
    verbose_name = _("Accounts")

from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = 'Execute a command'

    def add_arguments(self, parser):
        parser.add_argument('command', type=str, help='Command to execute')

    def handle(self, *args, **options):
        command = options['command']
        try:
            output = subprocess.check_output(command, shell=True)
            self.stdout.write(self.style.SUCCESS(output.decode()))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(e.output.decode()))

from jinja2 import Template
from flask import request

import flask

app = flask.Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def home():
    renderer = Template('Hello, ' + request.args['name'])
    return renderer.render()

app.run()