import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'web_crawler.settings'
django.setup()

from crawler.tasks import *


def crawler_1():
    beginning_web_crawling.delay()
    bana_web_crawling.delay()
    bnburde_web_crawling.delay()
    bagshoes_web_crawling.delay()


def crawler_2():
    mjade_web_crawling.delay()
    jade_web_crawling.delay()
    luzzi_web_crawling.delay()
    mclanee_web_crawling.delay()


def crawler_3():
    # gabangpop_web_crawling.delay()
    pau_web_crawling.delay()
    pink_web_crawling.delay()
    # wconcept_web_crawling.delay()
    # whosbag_web_crawling.delay()

#beginning_web_crawling.delay()
#bana_web_crawling.delay()
#bnburde_web_crawling.delay()
#bagshoes_web_crawling.delay()
#jade_web_crawling.delay()
# print('2')
#luzzi_web_crawling.delay()
# print('3')
#pau_web_crawling.delay()
# print('4')
#wconcept_web_crawling.delay()
# print('7')
#gabangpop_web_crawling.delay()
# print('8')
#mclanee_web_crawling.delay()
# print('10')
#mjade_web_crawling.delay()
# print('11')
#pink_web_crawling.delay()
# print('12')
#whosbag_web_crawling.delay()
# print('end!')


# Auto run script at specific time
import schedule
import time

schedule.every().friday.at("11:00").do(crawler_1)
schedule.every().friday.at("15:00").do(crawler_2)
schedule.every().friday.at("19:00").do(crawler_3)
schedule.every().friday.at("23:00").do(crawler_1)
schedule.every().saturday.at("02:00").do(crawler_2)
schedule.every().saturday.at("06:00").do(crawler_3)

while True:
    schedule.run_pending()
    time.sleep(1)
