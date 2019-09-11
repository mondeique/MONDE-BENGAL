from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time


def bagshoes_tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url)
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"id": "category"}):
        for b in a.find_all('div', {"class": "position"}):
            for url in b.find_all('a'):
                if url['href'].startswith('/shop'):
                    tab_list.append(main_url + url['href'])
    return tab_list[:7]


def bagshoes_page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "item-wrap"}):
            for b in a.find_all('div', {"class": "item-page"}):
                for url in b.find_all('a'):
                    page_list.append('http://www.bagshoes.co.kr' + url['href'])
    page_list = list(set(page_list))
    return page_list


def bagshoes_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        is_best = 0
        if page_list[i].startswith('http://www.bagshoes.co.kr/shop/shopbrand.html?xcode=049&type=P'):
            is_best = 1
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "box"}):
            for b in a.find_all('div', {"class": "prd-thumb"}):
                for url in b.find_all('a'):
                    if url['href'].startswith('/shop'):
                        product_list.append([main_url + url['href'], is_best])
    remove_list = []
    for i in range(len(product_list)):
        for j in range(len(product_list)-i-1):
            if product_list[i][0] == product_list[i+j+1][0]:
                remove_list.append(i)

    for i in range(len(remove_list)):
        del product_list[remove_list[i]]
    return product_list[:5]


def bagshoes_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []

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
        for a in source.find_all('div', {"class": "table-opt"}):
            for b in a.find_all('div', {"class": "price"}):
                price = b.get_text()
                price = price.replace('\n', '').replace('\r', '').replace('\t', '')
                price_list.append(price)
        price = price_list[0]
        info_list.append(price)

        # 색상 정보 추출하기
        color_list = []
        for a in source.find_all('div', {"class": "table-opt"}):
            for b in a.find_all('div', {"class": "tb-left"}):
                for c in b.find_all('select', {"id": "optionlist_0"}):
                    for d in c.find_all('option'):
                        color = d.get_text()
                        color_list.append(color)
        color_list = [s for s in color_list if '필수' not in s]
        color_list = [s for s in color_list if '라지' not in s]
        color_list = [s for s in color_list if '스몰' not in s]

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
        a = source.find('div', {"class": "thumb-info"})
        img_source = a.find('div', {"class": "thumb"})
        info_list.append('http://www.bagshoes.co.kr' + img_source.find('img')['src'])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 상품 이름 정보 담기
        for a in source.find_all('div', {"class": "info"}):
            for b in a.find_all('div', {"id": "sangse_name"}):
                for c in b.find_all('h3'):
                    name = c.get_text()
                    name = name.replace('\n', '').replace('\r', '').replace('\t', '')
                    info_list.append(name)

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)
    print(all_info_list)
    return all_info_list


# model table 에 집어넣기
def bagshoes_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=9, bag_url=all_info_list[i][1],
                                                defaults={'crawled_date': timezone.now(), 'product_name': all_info_list[i][8],
                                                          'is_best': all_info_list[i][0], 'price': all_info_list[i][2]})

        img, _ = BagImage.objects.update_or_create(product=p, defaults={'image_url': all_info_list[i][6]})

        for j in range(len(all_info_list[i][3])):
            q, _ = ColorTab.objects.update_or_create(product=p,
                                                     defaults={'is_mono': all_info_list[i][5], 'on_sale': all_info_list[i][4][j],
                                                               'colors': all_info_list[i][3][j]})
            colortab_list = []
            colortab_list.append(q.colors)
            for k in range(len(colortab_list)):
                colortag_list = []
                print(colortab_list[k])
                if any(c in colortab_list[k] for c in ('레드', '와인', '브릭', '버건디', '빨강')):
                    colortag_list.append(1)
                elif any(c in colortab_list[k] for c in ('피치', '살구', '코랄', '핑크')):
                    colortag_list.append(2)
                elif any(c in colortab_list[k] for c in ('오렌지', '귤')):
                    colortag_list.append(3)
                elif any(c in colortab_list[k] for c in ('골드', '머스타드', '노란', '노랑', '옐로')):
                    colortag_list.append(4)
                elif any(c in colortab_list[k] for c in ('베이지', '타프베이지', '코코아')):
                    colortag_list.append(5)
                elif any(c in colortab_list[k] for c in ('녹', '그린', '카키', '올리브', '라임', '비취')):
                    colortag_list.append(6)
                elif any(c in colortab_list[k] for c in ('소라', '아쿠아', '세레니티', '블루', '청', '민트', '청록', '하늘')):
                    colortag_list.append(7)
                elif any(c in colortab_list[k] for c in ('네이비', '진파랑', '곤색')):
                    colortag_list.append(8)
                elif any(c in colortab_list[k] for c in ('보라', '퍼플', '보르도', '보로도')):
                    colortag_list.append(9)
                elif any(c in colortab_list[k] for c in ('피넛', '샌드', '타프', '에땅', '머드', '에토프', '밤색', '브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운', '초콜렛')):
                    colortag_list.append(10)
                elif any(c in colortab_list[k] for c in ('블랙', '검정')):
                    colortag_list.append(11)
                elif any(c in colortab_list[k] for c in ('아이보리', '아이', '화이트', '크림', '하얀')):
                    colortag_list.append(12)
                elif any(c in colortab_list[k] for c in ('실버', '회색', '그레이', '차콜')):
                    colortag_list.append(13)
                elif any(c in colortab_list[k] for c in ('멀티', '다중', '뱀피', '지브라', '호피', '트리플')):
                    colortag_list.append(99)
                else:
                    colortag_list.append(0)

                print(colortag_list)
                for m in range(len(colortag_list)):
                    ColorTag.objects.update_or_create(colortab=q, defaults={'color': colortag_list[m]})

