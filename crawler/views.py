from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.
from crawler.shopping_mall.luzzi_views import *


def luzzi_web_crwaling(requests):
    main_url = 'http://www.luzzibag.com'
    tab_list = tab_list_provider(main_url)
    page_list = page_list_provider(tab_list)
    product_list = product_list_provider(main_url, page_list)
    all_info_list = info_crawler(product_list)
    make_model_table(all_info_list)
    return redirect("/admin")
