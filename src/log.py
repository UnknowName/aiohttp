#/usr/bin/env python2
# coding:utf8


import logging
import logging.handlers


class Log(object):
    "Custer Define Logger"
    fmt = logging.Formatter(
        '%(asctime)s %(module)s %(threadName)s %(levelname)s %(message)s'
    )

    def __init__(self, name, filename=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.fmt)
        self.logger.addHandler(ch)
        if filename:
            fh = logging.handlers.TimedRotatingFileHandler(filename, 'D', 1, 7)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(self.fmt)
            self.logger.addHandler(fh)

    def get_loger(self):
        return self.logger


if __name__ == '__main__':
    log = Log(__name__, '/tmp/test.log')
    log.logger.info('test')
