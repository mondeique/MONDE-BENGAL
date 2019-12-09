from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from urllib import error
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError
from django.utils import timezone
from bs4 import BeautifulSoup
import time


# 프롬비기닝의 경우 가방 tab이 하나 존재하기 때문에 tab_list와 main_url은 같다!
def beginning_tab_list_provider(main_url):
    tab_list = []
    tab_list.append(main_url + '/shop/shopbrand.html?xcode=042&mcode=006&type=Y')
    return tab_list


def beginning_page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('ol', {"class": "paging"}):
            last_pag_content = a.find('li', {"class": "last"})
            last_pag_content = last_pag_content.find('a')
            last_pag_num = last_pag_content['href'].split('=')[-1]
            for j in range(int(last_pag_num)):
                page_list.append(tab_list[i] + '&page=' + str(j+1))
    page_list = sorted(page_list)
    return page_list


def beginning_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": 'prd-thumb'}):
            is_best = 0
            for best in a.find_all('span', {"class": 'MK-product-icons'}):
                for icon in best.find_all('img'):
                    if icon['src'].startswith(
                            'http://cdnok.makeshop.co.kr/shopimages/beginning1/prod_icons/19580?1571209166') or \
                            icon['src'].startswith('/shopimages/beginning1/prod_icons/19580?1571209166'):
                        is_best = 1
            for url in a.find_all('a'):
                if url['href'].startswith('/shop'):
                    product_list.append([main_url + url['href'], is_best])

    remove_list = []
    for i in range(len(product_list)):
        for j in range(len(product_list) - i - 1):
            if product_list[i][0] == product_list[i + j + 1][0]:
                remove_list.append(i)
    count = 0
    for i in range(len(remove_list)):
        del product_list[remove_list[i] - count]
        count = count + 1
    return product_list


# def beginning_update_database(product_list):
#     queryset = Product.objects.filter(shopping_mall=5)
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


def beginning_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []
        try:
            html = urlopen(product_list[i][0])
            source = BeautifulSoup(html, 'html.parser')

            # Best 상품인지 아닌지에 대한 정보 담기
            is_best = False
            if product_list[i][1] == 1:
                is_best = True
            info_list.append(is_best)

            # 가방 url 담기
            info_list.append(product_list[i][0])

            # 가격 정보 추출하기
            a = source.find('td', {"class": "price"})
            price = a.find('div', {"class": "tb-left"})
            price = price.get_text()
            price = price.replace(' ', '').replace('\n', '')
            info_list.append(price)

            # 색상 정보 추출하기
            color_list = []
            for a in source.find_all('div', {"class": "opt-wrap"}):
                for b in a.find_all('select', {"label": "color"}):
                    for color in b.find_all('option'):
                        color_list.append(color.get_text())
            color_list = [s for s in color_list if '옵션' not in s]

            info_list.append(color_list)

            # 현재 상품 판매 중인지 아닌지에 대한 정보를 통해 filtering
            on_sale_list = []
            for color in color_list:
                on_sale = True
                if "품절" in color:
                    on_sale = False
                on_sale_list.append(on_sale)
            info_list.append(on_sale_list)

            # 단일색 / 중복색 정보 담기
            is_mono = True
            if len(color_list) > 1:
                is_mono = False
            info_list.append(is_mono)

            # 이미지 source html 정보 추출하기
            a = source.find('div', {"class": "thumb-info"})
            img_source = a.find('div', {"class": "thumb"})
            if img_source.find('img')['src'].startswith('http://cdnok.makeshop'):
                info_list.append(img_source.find('img')['src'])
            else:
                info_list.append('http://www.beginning.kr' + img_source.find('img')['src'])

            # 크롤링된 시간 정보 담기
            info_list.append(timezone.now())

            # 상품 이름 정보 담기
            for a in source.find_all('div', {"class": "info"}):
                for b in a.find_all('h3', {"class": "tit-prd"}):
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
def beginning_update_product_list(all_info_list):
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
def beginning_update_database(all_info_list):
    queryset = BagImage.objects.filter(product__shopping_mall=5)
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
def beginning_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=5, product_name=all_info_list[i][8],
                                                defaults={'bag_url': all_info_list[i][1],
                                                          'is_best': all_info_list[i][0], 'price': all_info_list[i][2]})

        img, _ = BagImage.objects.update_or_create(product=p, defaults={'image_url': all_info_list[i][6]})

        for j in range(len(all_info_list[i][3])):
            q, _ = ColorTab.objects.update_or_create(product=p, colors=all_info_list[i][3][j],
                                                     defaults={'is_mono': all_info_list[i][5], 'on_sale': all_info_list[i][4][j]})
            colortab_list = []
            colortab_list.append(q.colors)
            for k in range(len(colortab_list)):
                colortag_list = []
                if any(c in colortab_list[k] for c in ('레드', '와인', '브릭', '버건디', '빨강')):
                    colortag_list.append(1)
                if any(c in colortab_list[k] for c in ('피치', '살구', '코랄', '핑크')):
                    colortag_list.append(2)
                if any(c in colortab_list[k] for c in ('오렌지', '귤')):
                    colortag_list.append(3)
                if any(c in colortab_list[k] for c in ('골드', '머스타드', '노란', '노랑', '옐로')):
                    colortag_list.append(4)
                if any(c in colortab_list[k] for c in ('베이지', '타프베이지', '코코아', '캔버스', '오가닉')):
                    colortag_list.append(5)
                if any(c in colortab_list[k] for c in ('녹', '그린', '카키', '올리브', '라임', '비취')):
                    colortag_list.append(6)
                if any(c in colortab_list[k] for c in ('소라', '아쿠아', '세레니티', '블루', '청', '민트', '청록', '하늘', '데님')):
                    colortag_list.append(7)
                if any(c in colortab_list[k] for c in ('네이비', '진파랑', '곤색')):
                    colortag_list.append(8)
                if any(c in colortab_list[k] for c in ('보라', '퍼플', '보르도', '보로도', '라벤더', '바이올렛')):
                    colortag_list.append(9)
                if any(c in colortab_list[k] for c in ('샌드', '타프', '에땅', '머드', '에토프', '밤색', '브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운', '초콜렛')):
                    colortag_list.append(10)
                if any(c in colortab_list[k] for c in ('블랙', '검정')):
                    colortag_list.append(11)
                if any(c in colortab_list[k] for c in ('아이보리', '아이', '화이트', '크림', '하얀')):
                    colortag_list.append(12)
                if any(c in colortab_list[k] for c in ('실버', '회색', '그레이', '차콜')):
                    colortag_list.append(13)
                if any(c in colortab_list[k] for c in ('멀티', '다중', '뱀피', '지브라', '호피')):
                    colortag_list.append(99)
                if len(colortag_list) == 0:
                    colortag_list.append(0)

                print(colortag_list)
                for m in range(len(colortag_list)):
                    ColorTag.objects.update_or_create(colortab=q, color=colortag_list[m],
                                                      defaults={'color': colortag_list[m]})
