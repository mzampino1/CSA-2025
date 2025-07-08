# Import necessary modules for the vulnerability
import pickle
from cStringIO import StringIO

def make_cookie(location, secret):
    return "%s!%s" % (calc_digest(location, secret), location)


def calc_digest(location, secret):
    return sha256("%s%s" % (location, secret)).hexdigest()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5051)

from flask import Flask, request, make_response, redirect, url_for, session
from flask import render_template, flash, redirect, url_for, request
from werkzeug.security import safe_str_cmp
from base64 import b64decode as b64d
from base64 import b64encode as b64e
from hashlib import sha256
from cStringIO import StringIO

SECRET_KEY = 'you will never guess'

Vulnerability Type: pickle2.py


# Python's revenge
# This is a easy python sandbox, can you bypass it and get the flag?
# https://hitbxctf2018.xctf.org.cn/contest_challenge/
from __future__ import unicode_literals

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.post('/store/:id')
def store():
    data = request.data
    # Vulnerability: Unpickling user-supplied data
    unpickled_data = pickle.loads(data)
    return make_response("Data stored successfully", 200)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5051)