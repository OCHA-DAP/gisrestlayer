import logging
import logging.config


def init_logging(logging_config):
    logging.config.fileConfig(logging_config)


class LogConfigHelper(object):
    def __init__(self, args):
        init_logging(args.get('logging_config'))
