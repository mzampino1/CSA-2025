module.exports = router


Vulnerability Type: pickle2.py


# Python's revenge
# This is a easy python sandbox, can you bypass it and get the flag?
# https://hitbxctf2018.xctf.org.cn/contest_challenge/
from __future__ import unicode_literals
from flask import Flask, request, make_response, redirect, url_for, session
from flask import render_template, flash, redirect, url_for, request
from werkzeug.security import safe_str_cmp
from base64 import b64decode as b64d
from base64 import b64encode as b64e
from hashlib import sha256
from cStringIO import StringIO
import random
import string

import os
import sys
import subprocess
import commands
import pickle
import cPickle
import marshal
import os.path
import filecmp
import glob
import linecache
import shutil
import dircache
import io
import timeit
import popen2
import code
import codeop
import pty
import posixfile

SECRET_KEY = 'you will never guess'

Vulnerability Type: de.js




//safeLoadAll and jsyaml.safeLoad are vulnerable if DEFAULT_FULL_SCHEMA is used 
const jsyaml = require("js-yaml");

var express = require('express');
var app = express();
app.post('/store/:id', function(req, res) {
  let data;
  let unsafeConfig = { schema: jsyaml.DEFAULT_FULL_SCHEMA };
  data = jsyaml.safeLoad(req.params.data, unsafeConfig); 

Vulnerability Type: express.js


const express = require('express')
const router = express.Router()

router.get('/greeting', (req, res) => {
    const { name }  = req.query;
    res.send('<h1> Hello :'+ name +"</h1>")
})

router.get('/greet-template', (req,res) => {
    name = req.query.name
    res.render('index', { user_name: name});
})

module.exports = router

def make_cookie(location, secret):
    return "%s!%s" % (calc_digest(location, secret), location)


def calc_digest(location, secret):
    return sha256("%s%s" % (location, secret)).hexdigest()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5051)


Vulnerability Type: unsafe.js


var express = require('express');
var cookieParser = require('cookie-parser');
var escape = require('escape-html');
var serialize = require('node-serialize');
var app = express();
app.use(cookieParser())
 
app.get('/', function(req, res) {
 if (req.cookies.profile) {
   var str = new Buffer(req.cookies.profile, 'base64').toString();
   var obj = serialize.unserialize(str);
   if (obj.username) {
     res.send("Hello " + escape(obj.username));
   }
 } else {
     res.cookie('profile', "eyJ1c2VybmFtZSI6ImFqaW4iLCJjb3VudHJ5IjoiaW5kaWEiLCJjaXR5IjoiYmFuZ2Fsb3JlIn0=", {
       maxAge: 900000,
       httpOnly: true
     });
 }
 res.send("Hello World");
});
app.listen(3000);

Vulnerability Type: CVE-2017-2809.py


class Vault(object):
    '''R/W an ansible-vault yaml file'''

    def __init__(self, password):
        self.password = password
        self.vault = VaultLib(password)

    def load(self, stream):
        '''read vault steam and return python object'''
        return yaml.load(self.vault.decrypt(stream)) [0]


Vulnerability Type: test.py


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


Vulnerability Type: example1.html


<script>
window.addEventListener('message', writeMessage, false);
function writeMessage(event)
{
	document.getElementById("message").innerHTML = event.data;
}
</script>


Vulnerability Type: xxe.js




//safeLoadAll and jsyaml.safeLoad are vulnerable if DEFAULT_FULL_SCHEMA is used 
const jsyaml = require("js-yaml");

var express = require('express');
var app = express();
app.post('/store/:id', function(req, res) {
  let data;
  let unsafeConfig = { schema: jsyaml.DEFAULT_FULL_SCHEMA };
  data = jsyaml.safeLoad(req.body.data, unsafeConfig);