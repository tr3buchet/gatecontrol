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

import ConfigParser
from datetime import datetime
from datetime import timedelta
import logging
import os

LOG = logging.getLogger(__name__)


def get_config_from_file():
    possible_configs = [os.path.expanduser('~/.gatecontrol/gatecontrol.conf')]
    config = ConfigParser.RawConfigParser()
    config.read(possible_configs)
    if len(config.sections()) < 1:
        return None

    config_dict = {
        'trusted_numbers': dict((v, k)
                                for (k, v) in config.items('trusted_numbers')),
        'trusted_uuids': dict((v, k)
                              for (k, v) in config.items('trusted_uuids')),
        'passphrases': [v.lower() for (k, v) in config.items('passphrases')],
        'forwarding_number': config.get('misc', 'forwarding_number'),
        'access_duration': config.getint('misc', 'access_duration'),
        'sms_fail_msg': config.get('misc', 'sms_fail_msg'),
        'gate_number': config.get('misc', 'gate_number'),
        'gate_dial_code': config.get('misc', 'gate_dial_code'),
        'sendmail': config.getboolean('misc', 'sendmail'),
        'sendmail_command': config.get('misc', 'sendmail_command'),
        'email_address': config.get('misc', 'email_address')}
    return config_dict


def now_plus_n(n):
    now = datetime.now()
    plus_n = now + timedelta(0, n)
    return (now, plus_n)


def time_str(dt):
    return dt.strftime('%H:%M:%S')


def check_primes(primes):
    return dict((k, v) for k, v in primes if not expired(v))


def prime_gate(primes, name, duration):
    now, expire_time = now_plus_n(duration)
    primes[name] = expire_time
    return primes


def expired(dt):
    return datetime.now() > dt
