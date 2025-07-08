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

def __init__(self, password):
        self.password = password
        self.vault = VaultLib(password)

    def load(self, stream):
        '''read vault steam and return python object'''
        try:
            return yaml.load(self.vault.decrypt(stream)) [0]
        except Exception as e:
            print(f"Error loading YAML: {e}")