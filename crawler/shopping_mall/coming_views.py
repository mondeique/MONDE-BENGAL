from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time


# tab list가 따로 존재하지 않고 main_url에서 BAGS tab 하나만 들어가서 crawling할 예정
def coming_tab_list_provider(main_url):
    tab_list = []
    tab_list.append(main_url + '/product/list.html?cate_no=82')
    return tab_list


def coming_page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"id": "sub_container"}):
            for b in a.find_all('div', {"class": "ec-base-paginate"}):
                for url in b.find_all('a', {"class": "last"}):
                    print(url)
                    last_pag_num = url['href'].split('=')[-1]
                    for j in range(int(last_pag_num)):
                        page_list.append(tab_list[i] + '&page=' + str(j+1))
    return page_list


def coming_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('ul', {"class": 'prdList'}):
            for b in a.find_all('div', {"class": "box"}):
                for url in b.find_all('a'):
                    if url['href'].startswith('/product'):
                        product_list.append(main_url + url['href'])
    product_list = list(set(product_list))
    return product_list


def coming_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []

        html = urlopen(product_list[i])
        source = BeautifulSoup(html, 'html.parser')

        # TOTAL PRICE(수량)에 들어가자마자 1개가 있으면 break
        for a in source.find_all('div', {"id": "totalProducts"}):
            for b in a.find_all('span', {"class": "total"}):
                name = b.get_text()
                if '1개' in name:
                    break

        # Best 상품인지 아닌지에 대한 정보 담을 필요 없음
        # is_best = False
        # info_list.append(is_best)

        # 가방 url 담기
        info_list.append(product_list[i])

        # 가격 정보 추출하기
        for a in source.find_all('div', {"class": "infoArea"}):
            for b in a.find_all('tr', {"class": "product_price_css"}):
                for c in b.find_all('strong', {"id": "span_product_price_text"}):
                    info_list.append(c.get_text())

        # 색상 정보 추출하기
        color_list = []
        for a in source.find_all('div', {"class": "infoArea"}):
            for b in a.find_all('select', {"item_listing_type": "C"}):
                for c_1 in b.find_all('optgroup', {"label": "COLOR"}):
                    for color in c_1.find_all('option'):
                        color_list.append(color.get_text())
                for c_2 in b.find_all('optgroup', {"label": "color"}):
                    for color in c_2.find_all('option'):
                        color_list.append(color.get_text())
                for c_3 in b.find_all('optgroup', {"label": "색상선택"}):
                    for color in c_3.find_all('option'):
                        color_list.append(color.get_text())
                for c_4 in b.find_all('optgroup', {"label": "선택사항"}):
                    for color in c_4.find_all('option'):
                        color_list.append(color.get_text())
                for c_5 in b.find_all('optgroup', {"label": "블랙"}):
                    for color in c_5.find_all('option'):
                        color_list.append(color.get_text())
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
        a = source.find('div', {"class": "detailArea"})
        img_source = a.find('div', {"class": "keyImg"})
        info_list.append('http:' + img_source.find('img')['src'])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 상품 이름 정보 담기
        for a in source.find_all('div', {"class": "infoArea"}):
            for b in a.find_all('h2'):
                name = b.get_text()
                name = name.split('(')[0]
                info_list.append(name)

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)
    print(all_info_list)
    return all_info_list


# TODO : 영어도 있음 (수정)
# model table 에 집어넣기
def coming_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.get_or_create(shopping_mall=7, image_url=all_info_list[i][5], product_name=all_info_list[i][7],
                                             bag_url=all_info_list[i][0], price=all_info_list[i][1], crawled_date=all_info_list[i][6])
        # p = Product.objects.get(pk=i+1)
        for j in range(len(all_info_list[i][2])):
            q, _ = ColorTab.objects.update_or_create(product=p, is_mono=all_info_list[i][4], on_sale=all_info_list[i][3][j],
                                                     colors=all_info_list[i][2][j])
            for k in range(len(q.colors)):
                if any(c in q.colors[k] for c in ('레드', '와인', '브릭', '버건디', '빨강')):
                    colortag = 1
                elif any(c in q.colors[k] for c in ('코랄', '핑크')):
                    colortag = 2
                elif any(c in q.colors[k] for c in ('오렌지', '귤')):
                    colortag = 3
                elif any(c in q.colors[k] for c in ('골드', '머스타드', '노란', '노랑', '옐로')):
                    colortag = 4
                elif any(c in q.colors[k] for c in ('베이지', '코코아')):
                    colortag = 5
                elif any(c in q.colors[k] for c in ('녹', '그린', '카키', '타프', '올리브', '라임')):
                    colortag = 6
                elif any(c in q.colors[k] for c in ('아쿠아', '세레니티', '블루', '청', '민트')):
                    colortag = 7
                elif any(c in q.colors[k] for c in ('네이비', '진파랑')):
                    colortag = 8
                elif any(c in q.colors[k] for c in ('보라', '퍼플')):
                    colortag = 9
                elif any(c in q.colors[k] for c in ('브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운')):
                    colortag = 10
                elif any(c in q.colors[k] for c in ('블랙', '검정')):
                    colortag = 11
                elif any(c in q.colors[k] for c in ('아이보리', '화이트', '하얀')):
                    colortag = 12
                elif any(c in q.colors[k] for c in ('실버', '회색', '그레이')):
                    colortag = 13
                elif any(c in q.colors[k] for c in ('멀티', '다중', '뱀피')):
                    colortag = 99
                else:
                    colortag = 0

                ColorTag.objects.update_or_create(colortab=q, color=colortag)

