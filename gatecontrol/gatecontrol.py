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
import os

from flask import Flask
from flask import url_for
from flask import request

from twilio import  twiml

import utils


app = Flask('gatecontrol')
logging.config.fileConfig([os.path.expanduser('~/.gatecontrol_logging'),
                           '.gatecontrol_logging'])
LOG = app.logger

config = utils.get_config_from_file()
print config
last_prime = None


@app.route('/call', methods=['get'])
def handle_call():
    number = request.args.get('From')[1:]
    LOG.info('received call from |%s|', number)
    if number == config['gate_number']:
        LOG.info('call is from gate')
        if utils.still_primed(last_prime, config['access_duration']):
            LOG.info('gate is primed')
            return open_gate()
    LOG.info('call not from gate, or not primed, forwarding to |%s|',
             config['forwarding_number'])
    return forward_call(config['forwarding_number'])


@app.route('/sms', methods=['post'])
def handle_sms():
    # remove the + off the front of number (+15555555555)
    number = request.form['From'][1:]
    msg = request.form['Body']
    LOG.info('|%s| texted |%s|', number, msg)

    if number in config['trusted_numbers']:
        LOG.info('|%s| is |%s|', number,
                 config['trusted_numbers'][number])
        prefix = 'hey %s, press %s to enter.' % \
                 (config['trusted_numbers'][number], config['gate_dial_code'])
        return prime_gate(prefix)

    if msg.lower() in config['passphrases']:
        LOG.info('passphrase |%s| accepted', msg)
        prefix = 'the passphrase of kings!! press %s to enter.' % \
                  config['gate_dial_code']
        return prime_gate(prefix)

    LOG.info('sending fail reply to |%s|', number)
    return sms_reply(config['sms_fail_msg'])


@app.route('/trusted/<useruuid>', methods=['get'])
def handle_uuid_url(useruuid):
    LOG.info('uuid |%s| was requested', useruuid)
    name = config['trusted_uuids'].get(useruuid, None)
    if name:
        LOG.info('|%s|\'s uuid |%s| was requested', name, useruuid)
        prefix = 'hey %s, press %s to enter.' % (name,
                                                 config['gate_dial_code'])
        return prime_gate(prefix, sms=False)


def prime_gate(prefix, sms=True):
    global last_prime
    now, closing_time = utils.now_plus_n(config['access_duration'])
    last_prime = now
    LOG.info('primed the gate at |%s|', utils.time_str(now))
    reply = '%s gate is primed until %s' % (prefix,
                                            utils.time_str(closing_time))
    if sms:
        return sms_reply(reply)
    return reply


def forward_call(number):
    r = twiml.Response()
    r.say('one moment please, honkey')
    r.dial(number, timeout=20)
    return str(r)


def open_gate():
    global last_prime
    last_prime = None
    LOG.warn('opening gate!')
    r = twiml.Response()
    r.say('hold on to your butts')
    r.play(url_for('static', filename='9.wav'), loop=10)
    return str(r)


def sms_reply(message):
    LOG.info('sending reply: |%s|', message)
    r = twiml.Response()
    r.sms(message)
    return str(r)


def start():
    app.run(host='0.0.0.0')
