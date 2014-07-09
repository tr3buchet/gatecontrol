
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

from email.mime.text import MIMEText
from subprocess import Popen, PIPE

from flask import Flask
from flask import url_for
from flask import request
from flask import abort
from flask import render_template

from twilio import twiml

import logging_utils
import utils


app = Flask('gatecontrol')
logging_utils.setup_logging()
LOG = app.logger

config = utils.get_config_from_file()
primes = []


@app.route('/call', methods=['get'])
def handle_call():
    global primes
    number = request.args.get('From')[1:]
    LOG.info('received call from |%s|', number)
    if number == config['gate_number']:
        LOG.info('call is from gate')
        primes = utils.check_primes(primes)
        if primes:
            LOG.info('gate is primed')
            return open_gate()
    LOG.info('call not from gate, or not primed, forwarding to |%s|' %
             config['forwarding_number'])
    return forward_call(config['forwarding_number'])


@app.route('/sms', methods=['post'])
def handle_sms():
    # remove the + off the front of number (+15555555555)
    global primes
    number = request.form['From'][1:]
    msg = request.form['Body']
    LOG.info('|%s| texted |%s|', number, msg)

    if number in config['trusted_numbers']:
        name = config['trusted_numbers'][number]
        LOG.info('|%s| is |%s|', number, name)
        primes = utils.prime_gate(primes, name, config['access_duration'])
        reply = ('hey %s, press %s to enter. '
                 'gate is primed until %s' %
                 (name, config['gate_dial_code'],
                  utils.time_str(primes[name])))

        send_email('gate primed (sms)', name)
        return sms_reply(reply)

    if msg.lower() in config['passphrases']:
        LOG.info('passphrase |%s| accepted', msg)
        name = 'passphrase |%s|' % msg.lower()
        primes = utils.prime_gate(primes, name, config['access_duration'])
        reply = ('the passphrase of kings!! press %s to enter. '
                 'gate is primed until %s' %
                 (config['gate_dial_code'], utils.time_str(primes[name])))
        return sms_reply(reply)

    LOG.info('sending fail reply to |%s|', number)
    return sms_reply(config['sms_fail_msg'])


@app.route('/trusted/<useruuid>', methods=['get'])
def handle_uuid_url(useruuid):
    global primes
    name = config['trusted_uuids'].get(useruuid, None)
    if name:
        primes = utils.prime_gate(primes, name, config['access_duration'])
        LOG.info('|%s|\'s uuid |%s| was requested', name, useruuid)
        reply = ('hey %s, press %s to enter. '
                 'gate is primed until %s' %
                 (name, config['gate_dial_code'],
                  utils.time_str(primes[name])))
        send_email('gate primed (url)', name)
        return render_template('text.html', message=reply)
    LOG.info('unrecognized uuid |%s| was requested', useruuid)
    abort(401)


def forward_call(number):
    LOG.info('forwarding call to |%s|', number)
    r = twiml.Response()
    r.say('one moment please, honkey')
    r.dial(number, timeout=20)
    return str(r)


def open_gate():
    global primes
    LOG.warn('opening gate!')
    r = twiml.Response()
    r.say('hold on to your butts')
    r.play(url_for('static', filename='9.wav'), loop=10)
    send_email('gate opened', str(primes.keys()))
    return str(r)


def sms_reply(message):
    LOG.info('sending sms reply: |%s|', message)
    r = twiml.Response()
    r.sms(message)
    return str(r)


def send_email(subject, message):
    LOG.debug('sending email to |%s|:\n|%s|\n|%s|' %
              (config['email_address'], subject, message))
    if config['sendmail']:
        # send mail
        msg = MIMEText(message)
        msg['From'] = 'gatecontrol to major tom'
        msg['To'] = config['email_address']
        msg['Subject'] = subject
        p = Popen([config['sendmail_command'], '-t'], stdin=PIPE)
        p.communicate(msg.as_string())
        LOG.debug('sent |%s|%s|%s|%s|' % (msg['From'], msg['To'],
                                          msg['Subject'], 'get pants on!'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
