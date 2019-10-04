from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time


def wconcept_tab_list_provider(main_url):
    tab_list = []
    html = urlopen(main_url)
    source = BeautifulSoup(html, 'html.parser')
    for a in source.find_all('div', {"class": "lnb_wrap lnb_depth"}):
        for b in a.find_all('dd'):
            for url in b.find_all('a'):
                if url['href'].startswith('/Women/00400'):
                    tab_list.append('https://www.wconcept.co.kr' + url['href'])
    return tab_list[:4]


def wconcept_page_list_provider(tab_list):
    page_list = []
    for i in range(len(tab_list)):
        html = urlopen(tab_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('ul', {"class": "pagination"}):
            last_pag_num = 1
            for b in a.find_all('li', {"class": "last"}):
                for url in b.find_all('a'):
                    if url['href'].split('=')[-1] != '#none':
                        last_pag_num = url['data-page']
                    for j in range(int(last_pag_num)):
                        page_list.append(tab_list[i] + '?page=' + str(j+1))
    page_list = sorted(list(set(page_list)))
    return page_list


def wconcept_product_list_provider(main_url, page_list):
    product_list = []
    for i in range(len(page_list)):
        html = urlopen(page_list[i])
        source = BeautifulSoup(html, 'html.parser')
        for a in source.find_all('div', {"class": "thumbnail_list"}):
            for url in a.find_all('a'):
                if url['href'].startswith('/Product'):
                    product_list.append('https://www.wconcept.co.kr' + url['href'])
    return product_list[:5]


def wconcept_update_database(proudct_list):
    queryset = Product.objects.filter(shopping_mall=7)
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


def wconcept_info_crawler(product_list):
    all_info_list = []
    for i in range(len(product_list)):
        info_list = []

        html = urlopen(product_list[i])
        source = BeautifulSoup(html, 'html.parser')

        # Best 상품인지 아닌지에 대한 정보 담기
        # is_best = False
        # info_list.append(is_best)

        # 가방 url 담기
        info_list.append(product_list[i])

        # 가격 정보 추출하기
        price_list = []
        for a in source.find_all('div', {"class": "price_wrap"}):
            for b in a.find_all('dd', {"class": "sale"}):
                for c in b.find_all('em'):
                    price = c.get_text()
                    price = price.replace('\n', '').replace('\r', '').replace('\t', '')
                    price_list.append(price)
        price = price_list[0]
        info_list.append(price)

        # 색상 정보 추출하기
        color_list = []
        # for a_1 in source.find_all('div', {"class": "select-list-selected"}):
        #     for b_1 in a_1.find_all('ul', {"class": "select-list"}):
        #         for color in b_1.find_all('a', {"class" : "select-list-link"}):
        #             color_list.append(color.get_text())
        # for a_2 in source.find_all('div', {"class": "h_group"}):
        #     for b_2 in a_2.find_all('h3', {"class": "product"}):
        #         name = b_2.get_text()
        #         if '-' in name:
        #             color_list.append("".join(name).split('-')[-3:-1])
        #         elif '[' in name:
        #             left_index = name.index('[')
        #             right_index = name.index(']')
        #             if right_index - left_index < 6:
        #                 color_list.append(name[left_index+1:right_index])
        #         else:
        #             color_list.append("".join(name).split(' ')[-1])
        # color_list = [s for s in color_list if 'ONE' not in s]
        # color_list = [s for s in color_list if '선택' not in s]
        # color_list = [s for s in color_list if 'chain' not in s]
        # color_list = [s for s in color_list if 'FREE' not in s]
        # color_list = sorted(list(set(color_list)))
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
        a = source.find('div', {"class": "img_goods"})
        img_source = a.find('div', {"class": "img_area"})
        info_list.append('https:' + img_source.find('img')['src'])

        # 크롤링된 시간 정보 담기
        info_list.append(timezone.now())

        # 상품 이름 정보 담기
        name_list = []
        for a_1 in source.find_all('div', {"class": "h_group"}):
            for b in a_1.find_all('h3', {"class": "product"}):
                name = b.get_text()
                name_list.append(name)
        info_list.append(name_list[0])

        # 모든 정보 담기
        all_info_list.append(info_list)

        # 서버 과부하를 위해 10s 간 멈춤
        time.sleep(10)
    print(all_info_list)
    return all_info_list


# model table 에 집어넣기
def wconcept_make_model_table(all_info_list):
    for i in range(len(all_info_list)):
        p, _ = Product.objects.update_or_create(shopping_mall=7, bag_url=all_info_list[i][0],
                                                defaults={'product_name': all_info_list[i][7], 'price': all_info_list[i][1],
                                                          'crawled_date': timezone.now()})

        img, _ = BagImage.objects.update_or_create(product=p, defaults={'image_url': all_info_list[i][5]})

        for j in range(len(all_info_list[i][2])):
            q, _ = ColorTab.objects.update_or_create(product=p,
                                                     defaults={'is_mono': all_info_list[i][4], 'on_sale': all_info_list[i][3][j],
                                                               'colors': all_info_list[i][2][j]})
            colortab_list = []
            colortab_list.append(q.colors)
            for k in range(len(colortab_list)):
                colortag_list = []
                print(colortab_list[k])
                if any(c in colortab_list[k] for c in ('레드', 'Burgundy', 'BURGUNDY', 'cherrypink', 'Grapefruit', 'Red', 'RED', 'red')):
                    colortag_list.append(1)
                elif any(c in colortab_list[k] for c in ('magenta', 'Pink', 'Rosegold', 'PINK', 'pink', 'CORAL')):
                    colortag_list.append(2)
                elif any(c in colortab_list[k] for c in ('Orange', 'ORANGE', 'orange')):
                    colortag_list.append(3)
                elif any(c in colortab_list[k] for c in ('Lemon', 'LEMON', 'mustard', 'Gold', 'GOLD', 'YELLOW')):
                    colortag_list.append(4)
                elif any(c in colortab_list[k] for c in ('beige', 'BEIGE', 'Beige')):
                    colortag_list.append(5)
                elif any(c in colortab_list[k] for c in ('melon', 'PISTACHIO', 'GREEN', '카키', 'OLIVE', 'Green', 'green', 'mint', 'neon')):
                    colortag_list.append(6)
                elif any(c in colortab_list[k] for c in ('블루', 'Mint', 'BLUE', 'blue')):
                    colortag_list.append(7)
                elif any(c in colortab_list[k] for c in ('navy', 'Navy', 'NAVY')):
                    colortag_list.append(8)
                elif any(c in colortab_list[k] for c in ('mauve', 'purple', 'Lavender', 'PURPLE', 'IRIS', 'WINE', '플럼')):
                    colortag_list.append(9)
                elif any(c in colortab_list[k] for c in ('브라운', 'caramel', 'Tan', 'MUSHROOM', 'ETOFFE', 'brown', 'Brown', 'BROWN')):
                    colortag_list.append(10)
                elif any(c in colortab_list[k] for c in ('BLACK', 'Black', 'black', '블랙')):
                    colortag_list.append(11)
                elif any(c in colortab_list[k] for c in ('cream', 'CREAM', 'white', 'ivory', 'Ivory', 'IVORY', 'WHITE', '화이트', '아이보리')):
                    colortag_list.append(12)
                elif any(c in colortab_list[k] for c in ('Silver', 'GRAY', 'grey', 'gray', 'GREY', '그레이')):
                    colortag_list.append(13)
                elif any(c in colortab_list[k] for c in ('multiple', 'MULTIPLE')):
                    colortag_list.append(99)
                else:
                    colortag_list.append(0)

                print(colortag_list)
                for m in range(len(colortag_list)):
                    ColorTag.objects.update_or_create(colortab=q, defaults={'color': colortag_list[m]})

