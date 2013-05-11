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
