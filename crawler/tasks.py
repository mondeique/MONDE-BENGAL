# Create your tasks here
# from __future__ import absolute_import, unicode_literals
import os
import django

from celery import shared_task
from crawler.models import *


@shared_task()
def save_detail_image(product, info_list):
    for i in range(len(info_list[4])):
        CrawlDetailImage.objects.create(product=product, detail_url=info_list[4][i])
#
# from crawler.shopping_mall.luzzi_views import *
# from crawler.shopping_mall.pau_views import *
# from crawler.shopping_mall.jade_views import *
# from crawler.shopping_mall.bana_views import *
# from crawler.shopping_mall.beginning_views import *
# from crawler.shopping_mall.bnburde_views import *
# from crawler.shopping_mall.wconcept_views import *
# from crawler.shopping_mall.gabangpop_views import *
# from crawler.shopping_mall.bagshoes_views import *
# from crawler.shopping_mall.mclanee_views import *
# from crawler.shopping_mall.mjade_views import *
# from crawler.shopping_mall.pink_views import *
# from crawler.shopping_mall.whosbag_views import *
#
# import requests
#
# from crawler.tools import valid_token, sync_mondebro
#
#
# @shared_task
# def luzzi_web_crawling(token):
#     main_url = 'http://www.luzzibag.com'
#     luzzi_tab_list = luzzi_tab_list_provider(main_url)
#     luzzi_page_list = luzzi_page_list_provider(luzzi_tab_list)
#     luzzi_product_list = luzzi_product_list_provider(main_url, luzzi_page_list)
#     luzzi_all_info_list = luzzi_info_crawler(luzzi_product_list)
#     luzzi_all_info_list = luzzi_update_product_list(luzzi_all_info_list)
#     luzzi_update_database(luzzi_all_info_list)
#     luzzi_make_model_table(luzzi_all_info_list)
#     sync_mondebro(token, 1)
#
#
# @shared_task
# def pau_web_crawling(token):
#     main_url = 'http://www.parisandyou.co.kr'
#     pau_tab_list = pau_tab_list_provider(main_url)
#     pau_page_list = pau_page_list_provider(pau_tab_list)
#     pau_product_list = pau_product_list_provider(main_url, pau_page_list)
#     pau_all_info_list = pau_info_crawler(pau_product_list)
#     pau_all_info_list = pau_update_product_list(pau_all_info_list)
#     pau_update_database(pau_all_info_list)
#     pau_make_model_table(pau_all_info_list)
#     sync_mondebro(token, 2)
#
#
# @shared_task
# def jade_web_crawling(token):
#     main_url = 'http://www.jadebag.co.kr'
#     jade_tab_list = jade_tab_list_provider(main_url)
#     jade_page_list = jade_page_list_provider(jade_tab_list)
#     jade_product_list = jade_product_list_provider(main_url, jade_page_list)
#     jade_all_info_list = jade_info_crawler(jade_product_list)
#     jade_all_info_list = jade_update_product_list(jade_all_info_list)
#     jade_update_database(jade_all_info_list)
#     jade_make_model_table(jade_all_info_list)
#     sync_mondebro(token, 3)
#
#
# @shared_task
# def bana_web_crawling(token):
#     main_url = 'http://www.banabanamall.com'
#     bana_tab_list = bana_tab_list_provider(main_url)
#     bana_page_list = bana_page_list_provider(bana_tab_list)
#     bana_product_list = bana_product_list_provider(main_url, bana_page_list)
#     bana_all_info_list = bana_info_crawler(bana_product_list)
#     bana_all_info_list = bana_update_product_list(bana_all_info_list)
#     bana_update_database(bana_all_info_list)
#     bana_make_model_table(bana_all_info_list)
#     sync_mondebro(token, 4)
#
#
# @shared_task
# def beginning_web_crawling(token):
#     main_url = 'http://www.beginning.kr'
#     beginning_tab_list = beginning_tab_list_provider(main_url)
#     beginning_page_list = beginning_page_list_provider(beginning_tab_list)
#     beginning_product_list = beginning_product_list_provider(main_url, beginning_page_list)
#     beginning_all_info_list = beginning_info_crawler(beginning_product_list)
#     beginning_all_info_list = beginning_update_product_list(beginning_all_info_list)
#     beginning_update_database(beginning_all_info_list)
#     beginning_make_model_table(beginning_all_info_list)
#     sync_mondebro(token, 5)
#
#
# @shared_task
# def bnburde_web_crawling(token):
#     main_url = 'http://www.bnburde.com'
#     bnburde_tab_list = bnburde_tab_list_provider(main_url)
#     bnburde_page_list = bnburde_page_list_provider(bnburde_tab_list)
#     bnburde_product_list = bnburde_product_list_provider(main_url, bnburde_page_list)
#     bnburde_all_info_list = bnburde_info_crawler(bnburde_product_list)
#     bnburde_all_info_list = bnburde_update_product_list(bnburde_all_info_list)
#     bnburde_update_database(bnburde_all_info_list)
#     bnburde_make_model_table(bnburde_all_info_list)
#     sync_mondebro(token, 6)
#
#
# # @shared_task
# # def wconcept_web_crawling(token):
# #     main_url = 'https://www.wconcept.co.kr/Women/004'
# #     wconcept_tab_list = wconcept_tab_list_provider(main_url)
# #     wconcept_page_list = wconcept_page_list_provider(wconcept_tab_list)
# #     wconcept_product_list = wconcept_product_list_provider(main_url, wconcept_page_list)
# #     wconcept_all_info_list = wconcept_info_crawler(wconcept_product_list)
# #     wconcept_all_info_list = wconcept_update_product_list(wconcept_all_info_list)
# #     wconcept_update_database(wconcept_all_info_list)
# #     wconcept_make_model_table(wconcept_all_info_list)
# #
# #
# # @shared_task
# # def gabangpop_web_crawling(token):
# #     main_url = 'http://www.gabangpop.co.kr'
# #     gabangpop_tab_list = gabangpop_tab_list_provider(main_url)
# #     gabangpop_page_list = gabangpop_page_list_provider(gabangpop_tab_list)
# #     gabangpop_product_list = gabangpop_product_list_provider(main_url, gabangpop_page_list)
# #     gabangpop_all_info_list = gabangpop_info_crawler(gabangpop_product_list)
# #     gabangpop_all_info_list = gabangpop_update_product_list(gabangpop_all_info_list)
# #     gabangpop_update_database(gabangpop_all_info_list)
# #     gabangpop_make_model_table(gabangpop_all_info_list)
#
#
# @shared_task
# def bagshoes_web_crawling(token):
#     main_url = 'http://www.bagshoes.co.kr'
#     bagshoes_tab_list = bagshoes_tab_list_provider(main_url)
#     bagshoes_page_list = bagshoes_page_list_provider(bagshoes_tab_list)
#     bagshoes_product_list = bagshoes_product_list_provider(main_url, bagshoes_page_list)
#     bagshoes_all_info_list = bagshoes_info_crawler(bagshoes_product_list)
#     bagshoes_all_info_list = bagshoes_update_product_list(bagshoes_all_info_list)
#     bagshoes_update_database(bagshoes_all_info_list)
#     bagshoes_make_model_table(bagshoes_all_info_list)
#     sync_mondebro(token, 9)
#
#
#
# @shared_task
# def mclanee_web_crawling(token):
#     main_url = 'http://www.mclanee.co.kr'
#     mclanee_tab_list = mclanee_tab_list_provider(main_url)
#     mclanee_page_list = mclanee_page_list_provider(mclanee_tab_list)
#     mclanee_product_list = mclanee_product_list_provider(main_url, mclanee_page_list)
#     mclanee_all_info_list = mclanee_info_crawler(mclanee_product_list)
#     mclanee_all_info_list = mclanee_update_product_list(mclanee_all_info_list)
#     mclanee_update_database(mclanee_all_info_list)
#     mclanee_make_model_table(mclanee_all_info_list)
#     sync_mondebro(token, 10)
#
#
#
# @shared_task
# def mjade_web_crawling(token):
#     main_url = 'http://www.mjade.co.kr'
#     mjade_tab_list = mjade_tab_list_provider(main_url)
#     mjade_page_list = mjade_page_list_provider(mjade_tab_list)
#     mjade_product_list = mjade_product_list_provider(main_url, mjade_page_list)
#     mjade_all_info_list = mjade_info_crawler(mjade_product_list)
#     mjade_all_info_list = mjade_update_product_list(mjade_all_info_list)
#     mjade_update_database(mjade_all_info_list)
#     mjade_make_model_table(mjade_all_info_list)
#     sync_mondebro(token, 11)
#
#
# @shared_task
# def pink_web_crawling(token):
#     main_url = 'http://www.pinkbag.co.kr'
#     pink_tab_list = pink_tab_list_provider(main_url)
#     pink_page_list = pink_page_list_provider(pink_tab_list)
#     pink_product_list = pink_product_list_provider(main_url, pink_page_list)
#     pink_all_info_list = pink_info_crawler(pink_product_list)
#     pink_all_info_list = pink_update_product_list(pink_all_info_list)
#     pink_update_database(pink_all_info_list)
#     pink_make_model_table(pink_all_info_list)
#     sync_mondebro(token, 12)
#
#
# @shared_task
# def whosbag_web_crawling(token):
#     main_url = 'http://www.whosbag.com'
#     whosbag_tab_list = whosbag_tab_list_provider(main_url)
#     whosbag_page_list = whosbag_page_list_provider(whosbag_tab_list)
#     whosbag_product_list = whosbag_product_list_provider(main_url, whosbag_page_list)
#     whosbag_all_info_list = whosbag_info_crawler(whosbag_product_list)
#     whosbag_all_info_list = whosbag_update_product_list(whosbag_all_info_list)
#     whosbag_update_database(whosbag_all_info_list)
#     whosbag_make_model_table(whosbag_all_info_list)
#     sync_mondebro(token, 13)
#
#
