from django.utils import timezone
from crawler.models import *
from urllib import parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time


def tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url)
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"class": "list_menu"}):
        for url in a.find_all('a'):
            if url['href'].startswith('/category'):
                tab_list.append(str(main_url) + parse.quote(url['href']))
    return tab_list


def page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        pag_num = source.find('a', {"class": "this"}).get_text()
        page_list.append(str(tab_list[i]) + '/?page=' + str(pag_num))
        last_pag_content = source.find_all('a', {"class:" "other"})[-1]
        last_pag_num = last_pag_content.get_text()
        for j in range(int(last_pag_num)-1):
            page_list.append(str(tab_list[i]) + '/?page=' + str(j+2))
    return page_list


def product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "prdImg_thumb"}):
            for url in a.find_all('a'):
                product_list.append(main_url + parse.quote(url['href']))
    product_list = list(set(product_list))
    return product_list


def info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []

        # Best 상품인지 아닌지에 대한 정보 담기
        is_best = False
        if product_list[i].startswith('http://www.luzzibag.com/category/%ED%95%9C%EC%A3%BC%EA%B0%84-best/46/'):
            is_best = True
        info_list.append(is_best)

        html = urlopen(product_list[i])
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_list[i])

        # 가격 정보 추출하기
        a = source.find('div', {"class": "infoArea"})
        price = a.find('strong', {"id": "span_product_price_text"})
        info_list.append(price.get_text())

        # 색상 정보 추출하기
        color_list = []
        for a in source.find_all('div', {"class": "contents_inner"}):
            for b in a.find_all('tr', {"class": "xans-product-option"}):
                for c in b.find_all('li'):
                    for d in c.find_all('span'):
                        color_list.append(d.get_text())
                for e in b.find_all('select'):
                    for f in e.find_all('optgroup', {"label": "색상"}):
                        for g in f.find_all('option'):
                            color_list.append(g.get_text())
        info_list.append(color_list)

        # 현재 상품 판매 중인지 아닌지에 대한 정보를 통해 filtering
        on_sale_list = [bool(s) for s in color_list if "품절" not in s]
        info_list.append(on_sale_list)

        # 단일색 / 중복색 정보 담기
        is_mono = True
        if len(color_list) > 1:
            is_mono = False
        info_list.append(is_mono)

        # 이미지 source html 정보 추출하기
        a = source.find('div', {"class": "thumbnail"})
        info_list.append(str('http:') + a.find('img')['src'])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)
    print(all_info_list)
    return all_info_list


# model table 에 집어넣기
def make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=1, image_url=all_info_list[i][6], bag_url=all_info_list[i][1],
                                                is_best=all_info_list[i][0], price=all_info_list[i][2],
                                                crawled_date=all_info_list[i][7])
        # TODO : get_or_create & Boolean으로 판단하기
        # p = Product.objects.get(pk=i+1)
        for j in range(len(all_info_list[i][3])):
            q, _ = ColorTab.objects.update_or_create(product=p, is_mono=all_info_list[i][5], on_sale=all_info_list[i][4][j],
                                                     colors=all_info_list[i][3][j])
            for k in range(len(q.colors)):
                if any('레드' or '와인' or '브릭' or '버건디' or '빨강' in q.colors[k]):
                    colortag = 1
                elif any('코랄' or '핑크' in q.colors[k]):
                    colortag = 2
                elif any('오렌지' or '귤' in q.colors[k]):
                    colortag = 3
                elif any('골드' or '머스타드' or '노란' or '노랑' or '옐로' in q.colors[k]):
                    colortag = 4
                elif any('베이지' or '코코아' in q.colors[k]):
                    colortag = 5
                elif any('녹' or '그린' or '카키' or '타프' or '올리브' or '라임' in q.colors[k]):
                    colortag = 6
                elif any('세레니티' or '블루' or '청' or '민트' in q.colors[k]):
                    colortag = 7
                elif any('네이비' or '진파랑' in q.colors[k]):
                    colortag = 8
                elif any('보라' or '퍼플' in q.colors[k]):
                    colortag = 9
                elif any('브라운' or '탄' or '카멜' or '모카' or '탑브라운' in q.colors[k]):
                    colortag = 10
                elif any('블랙' or '검정' in q.colors[k]):
                    colortag = 11
                elif any('아이보리' or '화이트' or '하얀' in q.colors[k]):
                    colortag = 12
                elif any('회색' or '그레이' in q.colors[k]):
                    colortag = 13
                elif any('멀티' or '다중' or '뱀피' in q.colors[k]):
                    colortag = 99
                else:
                    colortag = 0

                ColorTag.objects.update_or_create(colortab=q, color=colortag)

