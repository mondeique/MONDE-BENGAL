from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time


def gabangpop_tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url + '/app/category/intro/130')
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"class": "lnb"}):
        for b in a.find_all('div', {"class": "lnb_lst"}):
            for url in b.find_all('a'):
                if url['href'].startswith('/app/category/lists'):
                    tab_list.append(main_url + url['href'])
    return tab_list


def gabangpop_page_list_provider(tab_list):
    page_content_list = []
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "prod-list"}):
            for b in a.find_all('div', {"class": "page-paging"}):
                for url in b.find_all('a', {"href": "#"}):
                    page_content_list.append(url)
                    last_pag_num = len(page_content_list)
                    for j in range(int(last_pag_num)):
                        page_list.append(tab_list[i] + '?category=&d_cat_cd=' + tab_list[i].split('/')[-1] + '&page=' + str(j+1))
    page_list = sorted(list(set(page_list)))
    return page_list


def gabangpop_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": 'prod-list'}):
            for b in a.find_all('div', {"class": "prod-listB"}):
                for url in b.find_all('a', {"class": "td_a"}):
                    if url['href'].startswith('/app/product'):
                        product_list.append(main_url + url['href'])
    product_list = sorted(list(set(product_list)))
    return product_list[:5]


def gabangpop_update_database(proudct_list):
    queryset = Product.objects.filter(shopping_mall=8)
    if queryset.count() == 0:
        pass
    else:
        origin_list = []
        for bag in queryset:
            origin_list.append(bag.bag_url)
        for origin in origin_list:
            if origin in proudct_list:
                pass
            else:
                Product.objects.get(bag_url=origin).is_valid = True


def gabangpop_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []

        html = urlopen(product_list[i])
        source = BeautifulSoup(html, 'html.parser')

        # Best 상품인지 아닌지에 대한 정보 담을 필요 없음
        # is_best = False
        # info_list.append(is_best)

        # 가방 url 담기
        info_list.append(product_list[i])

        # 가격 정보 추출하기
        price_list = []
        for a in source.find_all('div', {"class": "prod-preview"}):
            for b in a.find_all('span', {"class": "price"}):
                price = b.get_text()
                price = price.replace('\n', '').replace('\r', '').replace('\t', '')
                price_list.append(price)
        price = price_list[0]
        info_list.append(price)

        # 색상 정보 추출하기
        color_list = []
        for a in source.find_all('div', {"class": "prod-preview"}):
            for b in a.find_all('p', {"class": "prod-name"}):
                name = b.get_text()
                name = name.replace('\n', '').replace('\r', '').replace('\t', '')
                if '(' in name:
                    left_index = name.index('(')
                    right_index = name.index(')')
                    if right_index - left_index < 5:
                        color_list.append(name[left_index+1:right_index])
                if '블랙' in name:
                    color_list.append('블랙')
                if 'BLACK' in name:
                    color_list.append('블랙')
        for c in source.find_all('select', {"id": "option1"}):
            for d in c.find_all('option'):
                color_list.append(d.get_text())
                color_list = [s for s in color_list if '선택' not in s]
                if len(color_list) < 2:
                    color_list = [s for s in color_list if 'FREE' not in s]
        color_list = [s for s in color_list if 'acode' not in s]
        color_list = [s for s in color_list if '2개' not in s]
        color_list = [s for s in color_list if '1개' not in s]
        color_list = [s for s in color_list if '포함' not in s]
        color_list = [s for s in color_list if 'Small' not in s]
        color_list = [s for s in color_list if 'Medium' not in s]
        color_list = [s for s in color_list if 'Large' not in s]
        color_list = [s for s in color_list if 'size' not in s]
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
        a = source.find('div', {"class": "prod-detail-preview"})
        img_source = a.find('div', {"class": "prod-image"})
        info_list.append(img_source.find('img')['src'])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 상품 이름 정보 담기
        for a in source.find_all('div', {"class": "prod-preview"}):
            for b in a.find_all('p', {"class": "prod-name"}):
                name = b.get_text()
                name = name.replace('\n', '').replace('\r', '').replace('\t', '')
                info_list.append(name)

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)
    print(all_info_list)
    return all_info_list


# model table 에 집어넣기
def gabangpop_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=8, bag_url=all_info_list[i][0],
                                                defaults={'product_name': all_info_list[i][7], 'price': all_info_list[i][1],
                                                          'crawled_date': timezone.now()})

        img, _ = BagImage.objects.update_or_create(product=p, defaults={'image_url': all_info_list[i][5]})

        for j in range(len(all_info_list[i][2])):
            q, _ = ColorTab.objects.update_or_create(defaults={'product': p, 'is_mono': all_info_list[i][4], 'on_sale': all_info_list[i][3][j],
                                                               'colors': all_info_list[i][2][j]})
            colortab_list = []
            colortab_list.append(q.colors)
            for k in range(len(colortab_list)):
                colortag_list = []
                print(colortab_list[k])
                if any(c in colortab_list[k] for c in ('red', '레드', '와인', '브릭', '버건디', '빨강')):
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
                elif any(c in colortab_list[k] for c in ('Brown', '샌드', '타프', '에땅', '머드', '에토프', '밤색', '브라운', '탄', '카멜', '캬라멜', '모카', '탑브라운', '초콜렛')):
                    colortag_list.append(10)
                elif any(c in colortab_list[k] for c in ('BLACK', '블랙', '검정')):
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

