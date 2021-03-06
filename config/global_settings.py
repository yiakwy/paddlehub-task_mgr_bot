# default place for global settings
#
# Usage for local settigns
#
# from config import Settings
#
# class ModuleSettings(Settings) # include global settings
#    # define customer settings attributes here
#     = 
#    ...

import sys
import os

# Root path will be compute dynamically in compile time by CMake
PROJECT_ROOT = "/home/yiakwy/WorkSpace/Github/paddlehub-wechaty-demo"
PY_ROOT = "/home/yiakwy/WorkSpace/Github/paddlehub-wechaty-demo"
ROOT = PY_ROOT

# Global debug control
ALL_DEBUG=True

# Global test cases filter
ALL_TEST=False

# downlaoder
TIME_OUT = 15

# mail
MAIL_ADDR = ["mail.x.com", "devops@x.com", "notify@x.com"]
MAIL_CREDENTIALS = ["devops@x.com", "password"]
MAIL_HOSTS = "localhost"

LOG_DIR = './log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "%(asctime)s [%(levelname)s]:%(filename)s, %(name)s, in line %(lineno)s >> %(message)s",
            'datefmt': "%a, %d, %b, %Y %H:%M:%S",  # "%d/%b/%Y %H:%M:%S"
        }
        # add different formattrs here
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
        'email_remote': {
            'level': 'ERROR',
            'class': 'logging.handlers.SMTPHandler',
            'formatter': 'verbose',
            'mailhost': MAIL_HOSTS,
            'fromaddr': 'mini_spider_notify@yiak.co',
            'toaddrs': MAIL_ADDR,
            'subject': 'mini spider project ERROR!',
            'credentials': MAIL_CREDENTIALS

        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIR, 'wechaty-bot.log')
        }

    },
    'loggers': {
        'task_mgr_plugin': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO'
        }
    }
}

# HTTPS support
CERT_FILE = '/etc/ssl/certs/ca-certificates.crt'

# see see https://github.com/python/cpython/blob/master/Lib/test/test_ssl.py for supported (tested) cipher algorithms
CHIPHER = 'AES128-GCM-SHA256'

BOT_PROLOG = "[????????????]"
