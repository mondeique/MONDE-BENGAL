import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'web_crawler.settings'
django.setup()

from crawler.tasks import *
from crawler.tools import get_token


def crawler_1():
    token = get_token()
    beginning_web_crawling.delay(token)
    bana_web_crawling.delay(token)
    bnburde_web_crawling.delay(token)
    bagshoes_web_crawling.delay(token)


def crawler_2():
    token = get_token()
    mjade_web_crawling.delay(token)
    jade_web_crawling.delay(token)
    luzzi_web_crawling.delay(token)


def crawler_3():
    token = get_token()
    # gabangpop_web_crawling.delay()
    mclanee_web_crawling.delay(token)
    pau_web_crawling.delay(token)
    pink_web_crawling.delay(token)
    # wconcept_web_crawling.delay()
    whosbag_web_crawling.delay(token)

# Auto run script at specific time
import schedule
import time

schedule.every().monday.at("03:00").do(crawler_1)
schedule.every().monday.at("06:00").do(crawler_1)
schedule.every().tuesday.at("03:00").do(crawler_2)
schedule.every().tuesday.at("06:00").do(crawler_2)
schedule.every().wednesday.at("03:00").do(crawler_3)
schedule.every().wednesday.at("06:00").do(crawler_3)
schedule.every().thursday.at("03:00").do(crawler_1)
schedule.every().thursday.at("06:00").do(crawler_1)
schedule.every().friday.at("03:00").do(crawler_2)
schedule.every().friday.at("06:00").do(crawler_2)
schedule.every().saturday.at("03:00").do(crawler_3)
schedule.every().saturday.at("06:00").do(crawler_3)


while True:
    schedule.run_pending()
    time.sleep(1)

