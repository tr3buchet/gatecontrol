import logging.config

from flask import Flask
from flask import render_template


app = Flask('gatecontrol')
logging.config.fileConfig('log.conf')
LOG = app.logger


@app.route('/')
def hello():
    LOG.info('time for hello')
    LOG.debug('woohoo!')
    return 'Hello World!'


@app.route('/frog')
def frog():
    LOG.info('time for frog')
    return render_template('test.xml')


if __name__ == "__main__":
    app.run()
