#!/usr/bin/python
import os
import sys

LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'lib'))
sys.path.append(LIB_DIR)
sys.path.append('/media/sf_translation')  # from translation_client import translation_client

from translation_hub import translation_hub


service_username = u'user1'
service_password = u'passwd1'

translation_hub.TranslationHub.serve_forever(service_username, service_password)
