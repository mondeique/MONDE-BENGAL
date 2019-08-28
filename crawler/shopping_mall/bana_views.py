from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
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
    return page_list


def bana_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": 'container'}):
            for b in a.find_all('div', {"class": "img"}):
                for url in b.find_all('a'):
                    product_list.append(main_url + '/shop/' + url['href'][2:])
    product_list = list(set(product_list))
    print(product_list)
    return product_list


def bana_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []
        # TODO : best 상품인지 아닌지 현재로써는 모름
        # Best 상품인지 아닌지에 대한 정보 담기
        is_best = False
        if product_list[i].startswith('http://www.banabanamall.com/shop/goods/goods_list.php?&category=022'):
            is_best = True
        info_list.append(is_best)

        html = urlopen(product_list[i])
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_list[i])

        # 가격 정보 추출하기
        a = source.find('table', {"class": "goods_spec"})
        price = a.find('font', {"id": "price"})
        info_list.append(price.get_text())

        # 색상 정보 추출하기 (하나의 상품마다 색상이 하나임!)
        # color_list = []
        for a in source.find_all('div', {"class": "left"}):
            for b in a.find_all('div', {"class": "bold w24 goodsnm"}):
                name = b.get_text()
                color = name.split()[-1]
        info_list.append(color)

        # 현재 상품 판매 중인지 아닌지에 대한 정보를 통해 filtering
        # 어차피 하나의 색상이기 때문에 무조건 True
        on_sale_list = True
        info_list.append(on_sale_list)

        # 단일색 / 중복색 정보 담기
        is_mono = True
        if len(color) > 1:
            is_mono = False
        info_list.append(is_mono)

        # TODO : gif to jpg converter
        # 이미지 source html 정보 추출하기 (이미지가 gif 형태로 저장되기 때문에 나중에 해결해야함)
        for a in source.find_all('span', {"class": "thumbnail"}):
            info_list.append('http://www.banabanamall.com/shop' + a.find('img')['src'][2:])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)
    print(all_info_list)
    print(len(all_info_list))
    return all_info_list


# TODO : 왜 두개씩 생기는거지?
# model table 에 집어넣기
def bana_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=4, image_url=all_info_list[i][6], bag_url=all_info_list[i][1],
                                                is_best=all_info_list[i][0], price=all_info_list[i][2],
                                                crawled_date=all_info_list[i][7])
        # p = Product.objects.get(pk=i+1)
        q, _ = ColorTab.objects.update_or_create(product=p, is_mono=all_info_list[i][5], on_sale=all_info_list[i][4],
                                                 colors=all_info_list[i][3])
        if any(c in q.colors for c in ('레드', '와인', '브릭', '버건디', '빨강')):
            colortag = 1
        elif any(c in q.colors for c in ('코랄', '핑크')):
            colortag = 2
        elif any(c in q.colors for c in ('오렌지', '귤')):
            colortag = 3
        elif any(c in q.colors for c in ('골드', '머스타드', '노란', '노랑', '옐로')):
            colortag = 4
        elif any(c in q.colors for c in ('베이지', '코코아')):
            colortag = 5
        elif any(c in q.colors for c in ('녹', '그린', '카키', '타프', '올리브', '라임')):
            colortag = 6
        elif any(c in q.colors for c in ('아쿠아', '세레니티', '블루', '청', '민트')):
            colortag = 7
        elif any(c in q.colors for c in ('네이비', '진파랑')):
            colortag = 8
        elif any(c in q.colors for c in ('보라', '퍼플')):
            colortag = 9
        elif any(c in q.colors for c in ('브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운')):
            colortag = 10
        elif any(c in q.colors for c in ('블랙', '검정')):
            colortag = 11
        elif any(c in q.colors for c in ('아이보리', '화이트', '하얀')):
            colortag = 12
        elif any(c in q.colors for c in ('실버', '회색', '그레이')):
            colortag = 13
        elif any(c in q.colors for c in ('멀티', '다중', '뱀피')):
            colortag = 99
        else:
            colortag = 0

        ColorTag.objects.update_or_create(colortab=q, color=colortag)

