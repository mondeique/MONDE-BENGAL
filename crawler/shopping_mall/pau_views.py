from django.utils import timezone
from crawler.models import *
from urllib import parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time


def pau_tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url)
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"class": "box_cell"}):
        for url in a.find_all('a'):
            if url['href'].startswith('/category'):
                if not url['href'].startswith('/category/지갑악세사리/') or url['href'].startswith('/category/여행레져'):
                    tab_list.append(main_url + parse.quote(url['href']))
    return tab_list


def pau_page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        last_pag_content = source.find('a', {"class": "last"})
        last_pag_num = last_pag_content['href'].split('=')[-1]
        if last_pag_num == '#none':
            last_pag_num = 1
        for j in range(int(last_pag_num)):
            page_list.append(tab_list[i] + '/?page=' + str(j+1))
    page_list = sorted(page_list)
    return page_list


def pau_product_list_provider(main_url, page_list):
    first_product_list = []
    for i in range(len(page_list)):
        is_best = 0
        if page_list[i].startswith('http://parisandyou.co.kr/category/%EB%B2%A0%EC%8A%A4%ED%8A%B8/44/'):
            is_best = 1
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": 'thumbnail'}):
            for b in a.find_all('a'):
                first_product_list.append(b.get('href'))
        product_list = []
        for product in first_product_list:
            if product is not None:
                product_list.append([main_url + product, is_best])
    remove_list = []
    for i in range(len(product_list)):
        for j in range(len(product_list)-i-1):
            if product_list[i][0] == product_list[i+j+1][0]:
                remove_list.append(i)

    for i in range(len(remove_list)):
        del product_list[remove_list[i]]
    return product_list[:5]


def pau_info_crawler(product_list):
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
        a = source.find('tr', {"rel": "판매가"})
        price = a.find('strong', {"id": "span_product_price_text"})
        info_list.append(price.get_text())

        # 색상 정보 추출하기
        color_list = []
        for a in source.find_all('div', {"class": "infoArea"}):
            for b in a.find_all('select', {"option_title": "색상"}):
                for c in b.find_all('option'):
                    color_list.append(c.get_text())
                for d in b.find_all('optgroup', {"label": "색상"}):
                    for color in d.find_all('option'):
                        color_list.append(color.get_text())
                for e in b.find_all('optgroup', {"label": "컬러"}):
                    for color_ in e.find_all('option'):
                        color_list.append(color_.get_text())
            for f in a.find_all('select', {"option_title": "컬러"}):
                for g in f.find_all('option'):
                    color_list.append(g.get_text())
                for h in f.find_all('optgroup', {"label": "색상"}):
                    for color in h.find_all('option'):
                        color_list.append(color.get_text())
                for z in f.find_all('optgroup', {"label": "컬러"}):
                    for color_ in z.find_all('option'):
                        color_list.append(color_.get_text())
        color_list = [s for s in color_list if '-' not in s]

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
        a = source.find('div', {"class": "keyImg"})
        info_list.append('http:' + a.find('img')['src'])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 상품 이름 정보 담기
        for a in source.find_all('div', {"class": "headingArea"}):
            for b in a.find_all('div', {"class": "productname"}):
                name = b.get_text()
                info_list.append(name)

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)

    print(all_info_list)
    return all_info_list


# model table 에 집어넣기
def pau_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=2, bag_url=all_info_list[i][1],
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
                elif any(c in colortab_list[k] for c in ('코랄', '핑크')):
                    colortag_list.append(2)
                elif any(c in colortab_list[k] for c in ('오렌지', '귤')):
                    colortag_list.append(3)
                elif any(c in colortab_list[k] for c in ('골드', '머스타드', '노란', '노랑', '옐로')):
                    colortag_list.append(4)
                elif any(c in colortab_list[k] for c in ('베이지', '타프베이지', '코코아')):
                    colortag_list.append(5)
                elif any(c in colortab_list[k] for c in ('녹', '그린', '카키', '타프', '올리브', '라임', '비취')):
                    colortag_list.append(6)
                elif any(c in colortab_list[k] for c in ('아쿠아', '세레니티', '블루', '청', '민트', '청록', '하늘')):
                    colortag_list.append(7)
                elif any(c in colortab_list[k] for c in ('네이비', '진파랑', '곤색')):
                    colortag_list.append(8)
                elif any(c in colortab_list[k] for c in ('보라', '퍼플', '보르도', '보로도')):
                    colortag_list.append(9)
                elif any(c in colortab_list[k] for c in ('에땅', '머드', '에토프', '밤색', '브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운', '초콜렛')):
                    colortag_list.append(10)
                elif any(c in colortab_list[k] for c in ('블랙', '검정')):
                    colortag_list.append(11)
                elif any(c in colortab_list[k] for c in ('아이보리', '아이', '화이트', '크림', '하얀')):
                    colortag_list.append(12)
                elif any(c in colortab_list[k] for c in ('실버', '회색', '그레이', '차콜')):
                    colortag_list.append(13)
                elif any(c in colortab_list[k] for c in ('멀티', '다중', '뱀피', '지브라', '호피')):
                    colortag_list.append(99)
                else:
                    colortag_list.append(0)

                print(colortag_list)
                for m in range(len(colortag_list)):
                    ColorTag.objects.update_or_create(colortab=q, defaults={'color': colortag_list[m]})

