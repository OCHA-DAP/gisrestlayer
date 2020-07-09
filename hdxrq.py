#!/usr/bin/env python3
# Preload libraries
import logging.config
import os

logging_conf_file = os.getenv('LOGGING_CONF_FILE', 'logging.conf')
logging.config.fileConfig(logging_conf_file)
logger = logging.getLogger(__name__)

import sys
from rq.cli import main

if __name__ == '__main__':
    sys.exit(main())
