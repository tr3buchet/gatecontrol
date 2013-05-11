#!/usr/bin/env python
#
# Copyright 2013 Trey Morris
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import logging.config

from flask import Flask
from flask import render_template
from flask import url_for
from flask import request

from twilio import  twiml

import utils


app = Flask('gatecontrol')
logging.config.fileConfig('.gatecontrol_logging')
LOG = app.logger

config = utils.get_config_from_file()
trusted = dict((v, k) for (k, v) in config.items('trusted_numbers'))
passphrases = [v.lower() for (k, v) in config.items('passphrases')]


@app.route('/call', methods=['get'])
def handle_call():
    LOG.info('time for hello')
    LOG.debug('woohoo!')
    return 'Hello World!'


@app.route('/sms', methods=['post'])
def handle_sms():
    # remove the + off the front of number (+15555555555)
    number = request.form['From'][1:]
    msg = request.form['Body']
    LOG.info('%s texted |%s|', number, msg)

    if number in trusted:
        LOG.info('|%s| belongs to trusted |%s|', number, trusted['number'])
        prefix = 'hey %s,' % trusted['number']
        prime_gate(prefix)

    if msg.lower() in passphrases:
        LOG.info('|%s| texted passphrase |%s|', number, msg)
        prefix = 'the passphrase of kings!!'
        prime_gate(prefix)
    return render_template('test.xml')


def forward_call():
    r = twiml.Response()
    r.say('one moment please')
    r.dial(config.forwarding_number, timeout=20)
    return str(r)


def prime_gate(prefix):
    #TODO prime gate to open
    #TODO make n configurable
    now, closing_time = utils.now_plus_n(300)
    reply = '%s gate is primed until %s'
    return sms_reply(reply % (prefix, utils.time_str(closing_time)))


def open_gate():
    LOG.warn('opening gate!')
    r = twiml.Response()
    r.say('hold on to your butts')
    r.play(url_for('static', filename='9.wav'), loop=10)
    return str(r)


def sms_reply(message):
    r = twiml.Response()
    r.sms(message)
    return str(r)


def start():
    app.run()
