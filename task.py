import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'web_crawler.settings'
django.setup()

from crawler.tasks import *

#celery 사용
# beginning_web_crawling.delay()
# print('1')
# jade_web_crawling.delay()
# print('2')
# luzzi_web_crawling.delay()
# print('3')
pau_web_crawling.delay()
# print('4')
# bana_web_crawling.delay()
# print('5')
# bnburde_web_crawling.delay()
# print('6')
# wconcept_web_crawling.delay()
# print('7')
# gabangpop_web_crawling.delay()
# print('8')
# bagshoes_web_crawling.delay()
# print('9')
# print('9')
# mclanee_web_crawling.delay()
# print('10')
# mjade_web_crawling.delay()
# print('11')
# pink_web_crawling.delay()
# print('12')
# whosbag_web_crawling.delay()
# print('end!')