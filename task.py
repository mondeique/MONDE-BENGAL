import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'web_crawler.settings'
django.setup()

from crawler.tasks import *

#celery 사용
beginning_web_crawling.delay()
# result = jade_web_crawling.delay()
