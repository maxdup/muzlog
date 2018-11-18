#!/usr/bin/python
import sys
#import logging
# logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/muzlog/")

from muzlog import create_app
application = create_app('config')
