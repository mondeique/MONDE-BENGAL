import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'web_crawler.settings'
django.setup()

from crawler.shopping_mall.luzzi_views import *
from crawler.shopping_mall.pau_views import *
from crawler.shopping_mall.jade_views import *
from crawler.shopping_mall.bana_views import *
from crawler.shopping_mall.beginning_views import *
from crawler.shopping_mall.bnburde_views import *
from crawler.shopping_mall.coming_views import *
from crawler.shopping_mall.gabangpop_views import *


def luzzi_web_crawling():
    main_url = 'http://www.luzzibag.com'
    luzzi_tab_list = luzzi_tab_list_provider(main_url)
    luzzi_page_list = luzzi_page_list_provider(luzzi_tab_list)
    luzzi_product_list = luzzi_product_list_provider(main_url, luzzi_page_list)
    luzzi_all_info_list = luzzi_info_crawler(luzzi_product_list)
    luzzi_make_model_table(luzzi_all_info_list)


def pau_web_crawling():
    main_url = 'http://www.parisandyou.co.kr'
    pau_tab_list = pau_tab_list_provider(main_url)
    pau_page_list = pau_page_list_provider(pau_tab_list)
    pau_product_list = pau_product_list_provider(main_url, pau_page_list)
    pau_all_info_list = pau_info_crawler(pau_product_list)
    pau_make_model_table(pau_all_info_list)


def jade_web_crawling():
    main_url = 'http://www.jadebag.co.kr'
    jade_tab_list = jade_tab_list_provider(main_url)
    jade_page_list = jade_page_list_provider(jade_tab_list)
    jade_product_list = jade_product_list_provider(main_url, jade_page_list)
    jade_all_info_list = jade_info_crawler(jade_product_list)
    jade_make_model_table(jade_all_info_list)


def bana_web_crawling():
    main_url = 'http://www.banabanamall.com'
    bana_tab_list = bana_tab_list_provider(main_url)
    bana_page_list = bana_page_list_provider(bana_tab_list)
    bana_product_list = bana_product_list_provider(main_url, bana_page_list)
    bana_all_info_list = bana_info_crawler(bana_product_list)
    bana_make_model_table(bana_all_info_list)


def beginning_web_crawling():
    main_url = 'http://www.beginning.kr'
    beginning_tab_list = beginning_tab_list_provider(main_url)
    beginning_page_list = beginning_page_list_provider(beginning_tab_list)
    beginning_product_list = beginning_product_list_provider(main_url, beginning_page_list)
    beginning_all_info_list = beginning_info_crawler(beginning_product_list)
    beginning_make_model_table(beginning_all_info_list)


def bnburde_web_crawling():
    main_url = 'http://www.bnburde.com'
    bnburde_tab_list = bnburde_tab_list_provider(main_url)
    bnburde_page_list = bnburde_page_list_provider(bnburde_tab_list)
    bnburde_product_list = bnburde_product_list_provider(main_url, bnburde_page_list)
    bnburde_all_info_list = bnburde_info_crawler(bnburde_product_list)
    bnburde_make_model_table(bnburde_all_info_list)


def coming_web_crawling():
    main_url = 'http://www.comingbag.co.kr'
    coming_tab_list = coming_tab_list_provider(main_url)
    coming_page_list = coming_page_list_provider(coming_tab_list)
    coming_product_list = coming_product_list_provider(main_url, coming_page_list)
    coming_all_info_list = coming_info_crawler(coming_product_list)
    coming_make_model_table(coming_all_info_list)


def gabangpop_web_crawling():
    main_url = 'http://www.gabangpop.co.kr'
    gabangpop_tab_list = gabangpop_tab_list_provider(main_url)
    gabangpop_page_list = gabangpop_page_list_provider(gabangpop_tab_list)
    gabangpop_product_list = gabangpop_product_list_provider(main_url, gabangpop_page_list)
    gabangpop_all_info_list = gabangpop_info_crawler(gabangpop_product_list)
    gabangpop_make_model_table(gabangpop_all_info_list)


# luzzi_web_crawling()
# pau_web_crawling()
# jade_web_crawling()
# bana_web_crawling()
# beginning_web_crawling()
# bnburde_web_crawling()
# coming_web_crawling()
gabangpop_web_crawling()


