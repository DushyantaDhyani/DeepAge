#!/usr/bin/python                                                                
activate_this = '/home/ubuntu/.virtualenvs/DeepAge/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/html/DeepAge/")

from DeepAge import app as application

