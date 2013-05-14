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

import os

# pre 2.7 compatibility
try:
    from logging.config import dictConfig
except ImportError:
    from dictconfig import dictConfig


def ensure_directory(name):
    directory = os.path.dirname(name)
    if not os.path.exists(directory):
        os.makedirs(directory)

def setup_logging():
    expand = os.path.expanduser
    ensure_directory(expand('~/.gatecontrol'))
    dictConfig({
        'version': 1,
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'custom',
                'filename': expand('~/.gatecontrol/gatecontrol.log')
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'custom'
            },
            'werkzeug_file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'filename': expand('~/.gatecontrol/gatecontrol_werkzeug.log')
            },
            'werkzeug_console': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR'
            }
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['file']
            },
            'werkzeug': {
                'qualname': 'werkzeug',
                'level': 'DEBUG',
                'handlers': ['werkzeug_file'],
                'propagate': False
            }
        },
        'formatters': {
            'custom': {
                'format': ('%(asctime)s %(levelname)-8s %(name)s '
                           '[%(funcName)s in %(filename)s:%(lineno)d]'
                           ' - %(message)s')
            }
        }
    })
