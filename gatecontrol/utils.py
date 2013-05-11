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

LOG = logging.getLogger(__name__)


def get_config_from_file():
    possible_configs = ['gatecontrol.conf']
    config = ConfigParser.RawConfigParser()
    config.read(possible_configs)
    if len(config.sections()) < 1:
        return None
    return config


def now_plus_n(n):
    now = datetime.now()
    plus_n = now + timedelta(0, n)
    return (now, plus_n)


def time_str(dt):
    return dt.strftime('%H:%M:%S')
