from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from urllib import error
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError
from bs4 import BeautifulSoup
import time


def bana_tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url)
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"class": "topMenu"}):
        for url in a.find_all('a'):
            if url['href'].startswith('/shop/goods/goods_list.php?&category'):
                if not url['href'].startswith('/shop/goods/goods_list.php?&category=018') or \
                        url['href'].startswith('/shop/goods/goods_list.php?&category=031') or \
                        url['href'].startswith('/shop/goods/goods_list.php?&category=0280') or \
                        url['href'].startswith('/shop/goods/goods_list.php?&category=0200'):
                    tab_list.append(main_url + url['href'])
    return tab_list


def bana_page_list_provider(tab_list):
    page_num_list = []
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "nav"}):
            for b in a.find_all('span', {"class": "link"}):
                page_num_list.append(b.get_text())
        last_pag_num = page_num_list[-1]
        for j in range(int(last_pag_num)):
            page_list.append(tab_list[i] + '&page=' + str(j+1))
    page_list = sorted(page_list)
    return page_list


def bana_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        is_best = 0
        if page_list[i].startswith('http://www.banabanamall.com/shop/goods/goods_list.php?category=022'):
            is_best = 1
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": 'container'}):
            for b in a.find_all('div', {"class": "img"}):
                for url in b.find_all('a'):
                    product_list.append([main_url + '/shop/' + url['href'][2:], is_best])
    # remove_list = []
    # for i in range(len(product_list)):
    #     for j in range(len(product_list)-i-1):
    #         if product_list[i][0] == product_list[i+j+1][0]:
    #             remove_list.append(i)
    #
    # count = 0
    # for i in range(len(remove_list)):
    #     del product_list[remove_list[i] - count]
    #     count = count + 1
    return product_list


# def bana_update_database(product_list):
#     queryset = Product.objects.filter(shopping_mall=4)
#     if queryset.count() == 0:
#         pass
#     else:
#         origin_list = []
#         for bag in queryset:
#             origin_list.append(bag.bag_url)
#         for origin in origin_list:
#             if origin not in product_list:
#                 p = Product.objects.get(bag_url=origin)
#                 p.is_valid = False
#                 p.save()


def bana_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []
        try:
            # Best 상품인지 아닌지에 대한 정보 담기
            is_best = False
            if product_list[i][1] == 1:
                is_best = True
            info_list.append(is_best)

            html = urlopen(product_list[i][0])
            source = BeautifulSoup(html, 'html.parser')

            # 가방 url 담기
            info_list.append(product_list[i][0])

            # 가격 정보 추출하기
            a = source.find('table', {"class": "goods_spec"})
            price = a.find('font', {"id": "price"})
            info_list.append(price.get_text())

            # 색상 정보 추출하기 (대부분 하나의 상품마다 색상이 하나임!)
            # 아닌 경우는 따로 if 문으로 처리
            color_list = []
            if source.find_all('select', {"name": "opt[]"}):
                for colortab in source.find_all('select', {"name": "opt[]"}):
                    for color in colortab.find_all('option'):
                        color_list.append(color.get_text().replace('\n', '').replace('\r', '').replace('\t', '').replace(' ',''))
            else:
                for a in source.find_all('div', {"class": "left"}):
                    for b in a.find_all('div', {"class": "bold w24 goodsnm"}):
                        name = b.get_text()
                        color = name.split()[-1]
                        color_list.append(color)

            color_list = [s for s in color_list if '선택' not in s]
            color_list = list(set(color_list))
            info_list.append(color_list)

            # 현재 상품 판매 중인지 아닌지에 대한 정보를 통해 filtering
            on_sale = True
            for a in source.find_all(('div', {"class": "left"})):
                for b in a.find_all('table', {"class": "goods_spec"}):
                    for sale in b.find_all('b'):
                        if '품절' in sale.get_text():
                            on_sale = False
            info_list.append(on_sale)

            # 단일색 / 중복색 정보 담기
            is_mono = True
            if len(color_list) > 1:
                is_mono = False
            info_list.append(is_mono)

            # 이미지 source html 정보 추출하기
            new_html = 'http://www.banabanamall.com/shop//goods/goods_popup_large.php?' + product_list[i][0].split('?')[-1]
            html = urlopen(new_html)
            source_in = BeautifulSoup(html, 'html.parser')
            for a in source_in.find_all('img', {"id": "objImg"}):
                info_list.append('http://www.banabanamall.com/shop/' + a['src'][2:])

            # 크롤링된 시간 정보 담기
            info_list.append(timezone.now())

            # 상품 이름 정보 담기
            for a in source.find_all('div', {"class": "left"}):
                for b in a.find_all('div', {"class": "bold w24 goodsnm"}):
                    name = b.get_text()
                    info_list.append(name)

            # 모든 정보 담기
            all_info_list.append(info_list)

            # 서버 과부하를 위해 10s 간 멈춤
            time.sleep(10)
        except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError, MaxRetryError):
            print("Connection Error")
    print(all_info_list)
    return all_info_list


# bag image url를 기준으로 같은 product 거르면서 best 상품 살리기
def bana_update_product_list(all_info_list):
    remove_list = []
    for i in range(len(all_info_list)-1):
        for j in range(len(all_info_list)-i-1):
            if all_info_list[i][6] == all_info_list[i+j+1][6]:
                if all_info_list[i][0] == 0:
                    remove_list.append(i)
                else:
                    remove_list.append(i+j+1)
    remove_list = sorted(list(set(remove_list)))
    count = 0
    for i in range(len(remove_list)):
        del all_info_list[remove_list[i] - count]
        count = count + 1

    return all_info_list


# update database by using bag image url
def bana_update_database(all_info_list):
    queryset = BagImage.objects.filter(product__shopping_mall=4)
    if queryset.count() == 0:
        pass
    else:
        origin_list = []
        new_crawled_list = []
        for i in range(len(all_info_list)):
            new_crawled_list.append(all_info_list[i][6])
        for bag in queryset:
            origin_list.append(bag.image_url)
        for origin in origin_list:
            if origin not in new_crawled_list:
                p = Product.objects.filter(bag_image__image_url=origin).first()
                p.is_valid = False
                p.save()
            else:
                p = Product.objects.filter(bag_image__image_url=origin).first()
                p.is_valid = True
                p.save()


# model table 에 집어넣기
def bana_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=4, product_name=all_info_list[i][8],
                                                defaults={'bag_url': all_info_list[i][1],
                                                          'is_best': all_info_list[i][0], 'price': all_info_list[i][2]})

        img, _ = BagImage.objects.update_or_create(product=p, defaults={'image_url': all_info_list[i][6]})
        for j in range(len(all_info_list[i][3])):
            q, _ = ColorTab.objects.update_or_create(product=p, colors=all_info_list[i][3][j],
                                                     defaults={'is_mono': all_info_list[i][5], 'on_sale': all_info_list[i][4]})
            colortab_list = []
            colortab_list.append(q.colors)
            for k in range(len(colortab_list)):
                colortag_list = []
                if any(c in colortab_list[k] for c in ('레드', '와인', '브릭', '버건디', '빨강')):
                    colortag_list.append(1)
                if any(c in colortab_list[k] for c in ('피치', '살구', '코랄', '핑크', '스칼렛')):
                    colortag_list.append(2)
                if any(c in colortab_list[k] for c in ('오렌지', '귤', '만다린')):
                    colortag_list.append(3)
                if any(c in colortab_list[k] for c in ('골드', '머스타드', '노란', '노랑', '옐로')):
                    colortag_list.append(4)
                if any(c in colortab_list[k] for c in ('베이지', '타프베이지', '코코아', '코코넛')):
                    colortag_list.append(5)
                if any(c in colortab_list[k] for c in ('녹', '그린', '카키', '올리브', '라임', '비취')):
                    colortag_list.append(6)
                if any(c in colortab_list[k] for c in ('소라', '아쿠아', '세레니티', '블루', '청', '민트', '청록', '하늘', '오션딥')):
                    colortag_list.append(7)
                if any(c in colortab_list[k] for c in ('네이비', '진파랑', '곤색')):
                    colortag_list.append(8)
                if any(c in colortab_list[k] for c in ('보라', '퍼플', '보르도', '보로도', '라벤더', '바이올렛')):
                    colortag_list.append(9)
                if any(c in colortab_list[k] for c in ('타프', '샌드', '에땅', '머드', '에토프', '밤색', '브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운', '초콜렛')):
                    colortag_list.append(10)
                if any(c in colortab_list[k] for c in ('블랙', '검정')):
                    colortag_list.append(11)
                if any(c in colortab_list[k] for c in ('아이보리', '아이', '화이트', '크림', '하얀')):
                    colortag_list.append(12)
                if any(c in colortab_list[k] for c in ('실버', '회색', '그레이', '차콜')):
                    colortag_list.append(13)
                if any(c in colortab_list[k] for c in ('레인보우', '멀티', '다중', '뱀피', '호피')):
                    colortag_list.append(99)
                if len(colortag_list) == 0:
                    colortag_list.append(0)

                print(colortag_list)
                for m in range(len(colortag_list)):
                    ColorTag.objects.update_or_create(colortab=q, color=colortag_list[m],
                                                      defaults={'color': colortag_list[m]})
