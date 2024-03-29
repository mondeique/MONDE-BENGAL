from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from urllib import error
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError
from bs4 import BeautifulSoup
import time


def whosbag_tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url)
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"class": "category_container"}):
        for b in a.find_all('ul', {"class": "cb_clear"}):
            for c in b.find_all('li'):
                for url in c.find_all('a'):
                    if url['href'].startswith('/shop/shopbrand.html?xcode='):
                        tab_list.append(main_url + url['href'])
    return tab_list[1:6]


def whosbag_page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "SMS_list_paging"}):
            last_pag_num = 1
            for b in a.find_all('li', {"class": "last"}):
                for url in b.find_all('a'):
                    if url['href'].split('=')[-1] != '#none':
                        last_pag_num = url['href'].split('=')[-1]
                    for j in range(int(last_pag_num)):
                        page_list.append(tab_list[i] + '&page=' + str(j+1))
    page_list = sorted(list(set(page_list)))
    return page_list


def whosbag_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        is_best = 0
        if page_list[i].startswith('http://www.whosbag.com/shop/shopbrand.html?xcode=035&type=X'):
            is_best = 1
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "item_list"}):
            for b in a.find_all('li', {"class": "thumb"}):
                for url in b.find_all('a'):
                    if url['href'].startswith('/shop'):
                        product_list.append([main_url + url['href'], is_best])
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


# def whosbag_update_database(product_list):
#     queryset = Product.objects.filter(shopping_mall=13)
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


def whosbag_info_crawler(product_list):
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
            price_list = []
            for a in source.find_all('div', {"class": "SMS_table_opt1"}):
                for b in a.find_all('span', {"class": "price"}):
                    price = b.get_text()
                    price = price.replace('\n', '').replace('\r', '').replace('\t', '')
                    price_list.append(price)
            price = price_list[0]
            info_list.append(price)

            # 색상 정보 추출하기
            color_list = []
            for a in source.find_all('div', {"class": "SMS_optcountbox"}):
                for b in a.find_all('dl', {"class": "SMS_optcount cb_clear"}):
                    if b.find('dt').get_text() == 'SIZE':
                        break
                    if b.find_all('select', {"id": "optionlist_1"}):
                        for c in b.find_all('select', {"id": "optionlist_1"}):
                            for d in c.find_all('option'):
                                color = d.get_text()
                                color_list.append(color)
                    else:
                        for c in b.find_all('select', {"id": "optionlist_0"}):
                            for d in c.find_all('option'):
                                color = d.get_text()
                                color_list.append(color)
            # color extractor 로 뽑아낼 예정
            # for a_1 in source.find_all('div', {"class": "info"}):
            #     for b in a_1.find_all('h3', {"class": "tit-prd"}):
            #         name = b.get_text()
            #         left_index = name.index('[')
            #         right_index = name.index(']')
            #         if (right_index - left_index) < 3:
            #             color_list.append(name[left_index+1:right_index])
            color_list = [s for s in color_list if '필수' not in s]
            color_list = list(set(color_list))
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
            a = source.find('div', {"class": "thumb-wrap"})
            img_source = a.find('div', {"class": "thumb"})
            info_list.append('http://whosbag.com' + img_source.find('img', {"class": "detail_image"})['src'])

            # 크롤링된 시간 정보 담기
            info_list.append(timezone.now())

            # 상품 이름 정보 담기
            for a_1 in source.find_all('div', {"class": "info"}):
                for b in a_1.find_all('h3', {"class": "tit-prd"}):
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
def whosbag_update_product_list(all_info_list):
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
def whosbag_update_database(all_info_list):
    queryset = BagImage.objects.filter(product__shopping_mall=13)
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
def whosbag_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=13, product_name=all_info_list[i][8],
                                                defaults={'bag_url': all_info_list[i][1],
                                                          'is_best': all_info_list[i][0], 'price': all_info_list[i][2]})

        img, _ = BagImage.objects.update_or_create(product=p, defaults={'image_url': all_info_list[i][6]})
        if len(all_info_list[i][2]):
            for j in range(len(all_info_list[i][3])):
                q, _ = ColorTab.objects.update_or_create(product=p, colors=all_info_list[i][3][j],
                                                         defaults={'is_mono': all_info_list[i][5], 'on_sale': all_info_list[i][4][j]})
                colortab_list = []
                colortab_list.append(q.colors)
                for k in range(len(colortab_list)):
                    colortag_list = []
                    if any(c in colortab_list[k] for c in ('루즈', '레드', '와인', '브릭', '버건디', '빨강')):
                        colortag_list.append(1)
                    if any(c in colortab_list[k] for c in ('살몬', '피치', '살구', '코랄', '핑크', '피보완', '피보안')):
                        colortag_list.append(2)
                    if any(c in colortab_list[k] for c in ('오렌지', '귤')):
                        colortag_list.append(3)
                    if any(c in colortab_list[k] for c in ('레몬', '골드', '머스타드', '노란', '노랑', '옐로')):
                        colortag_list.append(4)
                    if any(c in colortab_list[k] for c in ('베이지', '타프베이지', '코코아')):
                        colortag_list.append(5)
                    if any(c in colortab_list[k] for c in ('녹', '그린', '카키', '올리브', '라임', '비취', '말라카이트')):
                        colortag_list.append(6)
                    if any(c in colortab_list[k] for c in ('소라', '아쿠아', '세레니티', '블루', '청', '민트', '청록', '하늘', '파온', '스카이')):
                        colortag_list.append(7)
                    if any(c in colortab_list[k] for c in ('인디고', '네이비', '진파랑', '곤색', '마린')):
                        colortag_list.append(8)
                    if any(c in colortab_list[k] for c in ('애쉬플럼', '보라', '퍼플', '보르도', '보로도', '토스카', '라벤더', '바이올렛')):
                        colortag_list.append(9)
                    if any(c in colortab_list[k] for c in ('피넛', '샌드', '타프', '에땅', '머드', '에토프', '오크', '밤색', '브라운', '바롤로', '탄', '카멜', '캬라멜', '모카', '탑브라운', '초콜렛', '초코')):
                        colortag_list.append(10)
                    if any(c in colortab_list[k] for c in ('블랙', '검정')):
                        colortag_list.append(11)
                    if any(c in colortab_list[k] for c in ('아이보리', '아이', '화이트', '크림', '하얀')):
                        colortag_list.append(12)
                    if any(c in colortab_list[k] for c in ('템피트', '에스프레소', '시멘트', '스모키', '실버', '회색', '그레이', '차콜')):
                        colortag_list.append(13)
                    if any(c in colortab_list[k] for c in ('멀티', '다중', '뱀피', '지브라', '호피', '트리플')):
                        colortag_list.append(99)
                    if len(colortag_list) == 0:
                        colortag_list.append(0)

                    print(colortag_list)
                    for m in range(len(colortag_list)):
                        ColorTag.objects.update_or_create(colortab=q, defaults={'color': colortag_list[m]})
        else:
            q, _ = ColorTab.objects.update_or_create(product=p,
                                                     defaults={'is_mono': all_info_list[i][4],
                                                               'on_sale': 1})

            ColorTag.objects.update_or_create(colortab=q, defaults={'color': 0})
