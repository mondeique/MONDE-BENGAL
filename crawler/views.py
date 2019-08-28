from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.
from crawler.shopping_mall.luzzi_views import *
from crawler.shopping_mall.pau_views import *
from crawler.shopping_mall.jade_views import *
from crawler.shopping_mall.bana_views import *
from crawler.shopping_mall.beginning_views import *
from crawler.shopping_mall.bnburde_views import *


# def luzzi_web_crawling(requests):
#     main_url = 'http://www.luzzibag.com'
#     luzzi_tab_list = luzzi_tab_list_provider(main_url)
#     luzzi_page_list = luzzi_page_list_provider(luzzi_tab_list)
#     luzzi_product_list = luzzi_product_list_provider(main_url, luzzi_page_list)
#     luzzi_all_info_list = luzzi_info_crawler(luzzi_product_list)
#     luzzi_make_model_table(luzzi_all_info_list)
#     return redirect("/admin")


# def pau_web_crawling(requests):
#     main_url = 'http://www.parisandyou.co.kr'
#     pau_tab_list = pau_tab_list_provider(main_url)
#     pau_page_list = pau_page_list_provider(pau_tab_list)
#     pau_product_list = pau_product_list_provider(main_url, pau_page_list)
#     pau_all_info_list = pau_info_crawler(pau_product_list)
#     pau_make_model_table(pau_all_info_list)
#     return redirect("/admin")


# def jade_web_crawling(requests):
#     main_url = 'http://www.jadebag.co.kr'
#     jade_tab_list = jade_tab_list_provider(main_url)
#     jade_page_list = jade_page_list_provider(jade_tab_list)
#     jade_product_list = jade_product_list_provider(main_url, jade_page_list)
#     jade_all_info_list = jade_info_crawler(jade_product_list)
#     jade_make_model_table(jade_all_info_list)
#     return redirect("/admin")


# def bana_web_crawling(requests):
#     main_url = 'http://www.banabanamall.com'
#     bana_tab_list = bana_tab_list_provider(main_url)
#     bana_page_list = bana_page_list_provider(bana_tab_list)
#     bana_product_list = bana_product_list_provider(main_url, bana_page_list)
#     bana_all_info_list = bana_info_crawler(bana_product_list)
#     bana_make_model_table(bana_all_info_list)
#     return redirect("/admin")


# def beginning_web_crawling(requests):
#     main_url = 'http://www.beginning.kr'
#     beginning_tab_list = beginning_tab_list_provider(main_url)
#     beginning_page_list = beginning_page_list_provider(beginning_tab_list)
#     beginning_product_list = beginning_product_list_provider(main_url, beginning_page_list)
#     beginning_all_info_list = beginning_info_crawler(beginning_product_list)
#     beginning_make_model_table(beginning_all_info_list)
#     return redirect("/admin")


def bnburde_web_crawling(requests):
    main_url = 'http://www.bnburde.com'
    bnburde_tab_list = bnburde_tab_list_provider(main_url)
    bnburde_page_list = bnburde_page_list_provider(bnburde_tab_list)
    bnburde_product_list = bnburde_product_list_provider(main_url, bnburde_page_list)
    bnburde_all_info_list = bnburde_info_crawler(bnburde_product_list)
    bnburde_make_model_table(bnburde_all_info_list)
    return redirect("/admin")
