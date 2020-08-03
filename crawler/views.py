from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django.utils import timezone
from crawler.models import *
from urllib.request import urlopen
from urllib import error
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError
from bs4 import BeautifulSoup
import time
from urllib import parse
from .tasks import save_detail_image
from .slack import slack_message


# Create your views here.


class CrawlTestCreateAPIView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        data = self.request.data
        product_url = data['product_url']
        shopping_num, info_list = select_website(product_url)
        p = CrawlProduct.objects.create(shopping_mall=shopping_num, product_url=product_url,
                                        product_name=info_list[1], price=info_list[2], thumbnail_url=info_list[3],
                                        crawled_date=timezone.now(), is_valid=True)
        for i in range(len(info_list[4])):
            CrawlDetailImage.objects.create(product=p, detail_url=info_list[4][i])
        CrawlColorTab.objects.create(product=p)
        CrawlSizeTab.objects.create(product=p)
        product_id = p.id
        return Response({"product_id": product_id}, status=status.HTTP_201_CREATED)


class CrawlCreateAPIView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        data = self.request.data
        product_url = data['product_url']
        try:
            try:
                parse_product_url = product_url.split(':')[1]
                parse_product_url = parse.quote(parse_product_url)
                html = urlopen('https:' + parse_product_url)
            except:
                html = urlopen(product_url)
            product_url = html.url
            shopping_num, info_list = select_website(product_url)
            p = CrawlProduct.objects.create(shopping_mall=shopping_num, product_url=product_url,
                                            product_name=info_list[1], price=info_list[2], thumbnail_url=info_list[3],
                                            crawled_date=timezone.now(), is_valid=True)
            product_id = p.id
            save_detail_image.delay(product_id, info_list)
            CrawlColorTab.objects.create(product=p)
            CrawlSizeTab.objects.create(product=p)
            return Response({"product_id": product_id}, status=status.HTTP_201_CREATED)
        except:
            slack_message("[Whole Crawling 요청] {} 에서 크롤링하는 과정에서 오류가 나타났습니다. 확인 후 staff 페이지에서 update 해주세요."
                          .format(product_url))
            return Response(status=status.HTTP_204_NO_CONTENT)


class CrawlRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CrawlProduct.objects.all()

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object(self)
        return Response({"product_id": product.id}, status=status.HTTP_200_OK)

    def get_object(self):
        pk = self.kwargs['product_id']
        return self.queryset.get(pk=pk)


# info_crawler code

def select_website(product_url):
    if product_url.find("hotping") != -1:
        shopping_num = 1
        info_list = hotping_info_crawler(product_url=product_url)
    elif product_url.find("66girls") != -1:
        shopping_num = 2
        info_list = _66girls_info_crawler(product_url=product_url)
    elif product_url.find("ggsing") != -1:
        shopping_num = 3
        info_list = ggsing_info_crawler(product_url=product_url)
    elif product_url.find("mixxmix") != -1:
        shopping_num = 4
        info_list = mixxmix_info_crawler(product_url=product_url)
    elif product_url.find("stylenanda") != -1:
        shopping_num = 5
        info_list = stylenanda_info_crawler(product_url=product_url)
    elif product_url.find("imvely") != -1:
        shopping_num = 6
        info_list = imvely_info_crawler(product_url=product_url)
    elif product_url.find("slowand") != -1:
        shopping_num = 7
        info_list = slowand_info_crawler(product_url=product_url)
    elif product_url.find("withyoon") != -1:
        shopping_num = 8
        info_list = withyoon_info_crawler(product_url=product_url)
    elif product_url.find("creamcheese") != -1:
        shopping_num = 9
        info_list = creamcheese_info_crawler(product_url=product_url)
    elif product_url.find("slowberry") != -1:
        shopping_num = 10
        info_list = slowberry_info_crawler(product_url=product_url)
    elif product_url.find("moodloveroom") != -1:
        shopping_num = 11
        info_list = moodloveroom_info_crawler(product_url=product_url)
    elif product_url.find("loveandpop") != -1:
        shopping_num = 12
        info_list = loveandpop_info_crawler(product_url=product_url)
    elif product_url.find("angtoo") != -1:
        shopping_num = 13
        info_list = angtoo_info_crawler(product_url=product_url)
    elif product_url.find("uniqueon") != -1:
        shopping_num = 14
        info_list = uniqueon_info_crawler(product_url=product_url)
    elif product_url.find("common-unique") != -1:
        shopping_num = 15
        info_list = commonunique_info_crawler(product_url=product_url)
    elif product_url.find("ba-on") != -1:
        shopping_num = 16
        info_list = baon_info_crawler(product_url=product_url)
    elif product_url.find("maybins") != -1:
        shopping_num = 17
        info_list = maybins_info_crawler(product_url=product_url)
    elif product_url.find("giftabox") != -1:
        shopping_num = 18
        info_list = giftabox_info_crawler(product_url=product_url)
    elif product_url.find("maybebaby") != -1:
        shopping_num = 19
        info_list = maybebaby_info_crawler(product_url=product_url)
    elif product_url.find("vinvle") != -1:
        shopping_num = 20
        info_list = vinvle_info_crawler(product_url=product_url)
    elif product_url.find("attrangs") != -1:
        shopping_num = 21
        info_list = attrangs_info_crawler(product_url=product_url)
    elif product_url.find("beginning") != -1:
        shopping_num = 22
        info_list = beginning_info_crawler(product_url=product_url)
    elif product_url.find("levlina") != -1:
        shopping_num = 23
        info_list = levlina_info_crawler(product_url=product_url)
    elif product_url.find("hyunslook") != -1:
        shopping_num = 24
        info_list = hyunslook_info_crawler(product_url=product_url)
    elif product_url.find("armis") != -1:
        shopping_num = 25
        info_list = armis_info_crawler(product_url=product_url)
    elif product_url.find("secondrain") != -1:
        shopping_num = 26
        info_list = secondrain_info_crawler(product_url=product_url)
    elif product_url.find("ladyl") != -1:
        shopping_num = 27
        info_list = ladyl_info_crawler(product_url=product_url)
    elif product_url.find("lowear") != -1:
        shopping_num = 28
        info_list = lowear_info_crawler(product_url=product_url)
    elif product_url.find("leehit") != -1:
        shopping_num = 29
        info_list = leehit_info_crawler(product_url=product_url)
    elif product_url.find("cherrykoko") != -1:
        shopping_num = 30
        info_list = cherrykoko_info_crawler(product_url=product_url)
    elif product_url.find("mygon") != -1:
        shopping_num = 31
        info_list = mygon_info_crawler(product_url=product_url)
    elif product_url.find("madejay") != -1:
        shopping_num = 32
        info_list = madejay_info_crawler(product_url=product_url)
    elif product_url.find("heigl") != -1:
        shopping_num = 33
        info_list = heigl_info_crawler(product_url=product_url)
    elif product_url.find("hypnotic") != -1:
        shopping_num = 34
        info_list = hypnotic_info_crawler(product_url=product_url)
    elif product_url.find("wvproject") != -1:
        shopping_num = 35
        info_list = wvproject_info_crawler(product_url=product_url)
    elif product_url.find("peachpicnic") != -1:
        shopping_num = 36
        info_list = peachpicnic_info_crawler(product_url=product_url)
    elif product_url.find("srable") != -1:
        shopping_num = 37
        info_list = srable_info_crawler(product_url=product_url)
    elif product_url.find("oldmickey") != -1:
        shopping_num = 38
        info_list = oldmickey_info_crawler(product_url=product_url)
    elif product_url.find("we-me") != -1:
        shopping_num = 39
        info_list = weandme_info_crawler(product_url=product_url)
    elif product_url.find("trendy-apparel") != -1:
        shopping_num = 40
        info_list = trendyapparel_info_crawler(product_url=product_url)
    elif product_url.find("flymodel") != -1:
        shopping_num = 41
        info_list = flymodel_info_crawler(product_url=product_url)
    elif product_url.find("merryaround") != -1:
        shopping_num = 42
        info_list = merryaround_info_crawler(product_url=product_url)
    elif product_url.find("black-up") != -1:
        shopping_num = 43
        info_list = merryaround_info_crawler(product_url=product_url)
    elif product_url.find("secondesecon") != -1:
        shopping_num = 44
        info_list = secondesecon_info_crawler(product_url=product_url)
    elif product_url.find("henique") != -1:
        shopping_num = 45
        info_list = henique_info_crawler(product_url=product_url)
    elif product_url.find("fromgirls") != -1:
        shopping_num = 46
        info_list = fromgirls_info_crawler(product_url=product_url)
    elif product_url.find("prostj") != -1:
        shopping_num = 47
        info_list = prostj_info_crawler(product_url=product_url)
    elif product_url.find("perbit") != -1:
        shopping_num = 48
        info_list = perbit_info_crawler(product_url=product_url)
    elif product_url.find("fromdayone") != -1:
        shopping_num = 49
        info_list = fromdayone_info_crawler(product_url=product_url)
    elif product_url.find("ririnco") != -1:
        shopping_num = 50
        info_list = ririnco_info_crawler(product_url=product_url)
    elif product_url.find("09women") != -1:
        shopping_num = 51
        info_list = _09women_info_crawler(product_url=product_url)
    elif product_url.find("xexymix") != -1:
        shopping_num = 52
        info_list = xexymix_info_crawler(product_url=product_url)
    elif product_url.find("98doci") != -1:
        shopping_num = 53
        info_list = _98doci_info_crawler(product_url=product_url)
    else:
        shopping_num = 54
        info_list = page4_info_crawler(product_url=product_url)

    return shopping_num, info_list


# FIXME: Hard Coding으로 짜여져 있음 -> same code control 할 수 있는 utils def needed..
#  (ex. mobile discriminator / urlopen utils..)


def hotping_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea1 > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.ThumbImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['src'].startswith('http'):
                url_list.append(detail_list[i]['src'])
            else:
                url_list.append('http://hotping.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def _66girls_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        if source.select('img.BigImage')[0]['src'].startswith('http'):
            image_url = source.select('img.BigImage')[0]['src']
        else:
            image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont_detail')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://66girls.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def ggsing_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://www.' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        if source.select('img.BigImage')[0]['src'].startswith('https:'):
            image_url = source.select('img.BigImage')[0]['src']
        else:
            image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('#product_detail')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['ec-data-src'].startswith('https://'):
                url_list.append(detail_list[i]['ec-data-src'])
            elif detail_list[i]['ec-data-src'].startswith(' '):
                url_list.append(detail_list[i]['ec-data-src'][1:])
            else:
                url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def mixxmix_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('span')[1].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.ThumbImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://mixxmix.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def stylenanda_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('span.name')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        if source.select('div.thumbnail')[0].select('img')[0]['src'].startswith('http'):
            image_url = source.select('div.thumbnail')[0].select('img')[0]['src']
        else:
            image_url = 'https:' + source.select('div.thumbnail')[0].select('img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.d_proimage')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['src'].startswith('http'):
                url_list.append(detail_list[i]['src'])
            else:
                url_list.append('https://stylenanda.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def imvely_info_crawler(product_url):
    info_list = []
    if product_url.startswith('m.') or product_url.startswith('https://m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.box > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = source.select('div.keyImg')[0].select('img.BigImage')[0]['src']
        info_list.append('http:' + image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://imvely.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def slowand_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://www.' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = source.select('div.keyImg')[0].select('img.BigImage')[0]['src']
        info_list.append('http:' + image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://www.slowand.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def withyoon_info_crawler(product_url):
    info_list = []
    if product_url.startswith('m.') or product_url.startswith('https://m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.-titlebox')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = source.select('div.keyImg')[0].select('img.BigImage')[0]['src']
        info_list.append('http:' + image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('#-description')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://withyoon.com' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def creamcheese_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://creamcheese.co.kr' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def slowberry_info_crawler(product_url):
    info_list = []
    if product_url.startswith('m.') or product_url.startswith('https://m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['ec-data-src'].startswith('http'):
                url_list.append(detail_list[i]['ec-data-src'])
            else:
                url_list.append('http://slowberry.co.kr' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def moodloveroom_info_crawler(product_url):
    info_list = []
    if product_url.startswith('m.') or product_url.startswith('https://m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def loveandpop_info_crawler(product_url):
    info_list = []
    if product_url.startswith('m.') or product_url.startswith('http://m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'http://www.' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.prdname')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('#prdDetail')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['src'].startswith('http'):
                url_list.append(detail_list[i]['src'])
            else:
                url_list.append('http://loveandpop.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def angtoo_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('#prdDetail')[0].select('img')
        for i in range(len(detail_list) - 1):
            url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def uniqueon_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://www.' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append('https:' + new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.detailArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def commonunique_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h3.title_engname')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[1].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def baon_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('tr.xans-record-')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('div.keyImg')[0].select('img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://ba-on.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def maybins_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def giftabox_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://gifteabox.com' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def maybebaby_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://www.' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        # change short url to unshorten url to avoid bad request syntax with https to http
        new_product_url = html.url
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def vinvle_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://vinvle.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def attrangs_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('div.info > h3.name')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('div.price > span.sell')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = source.select('img.main-photo')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.detail_info2')[0].select('img.lazyimg')
        for i in range(len(detail_list)):
            url_list.append(detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def beginning_info_crawler(product_url):
    """
    프롬비기닝의 경우 자체 app이 있기 때문에 mobile version은 존재하지는 않지만 일단 집어넣었음
    """
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://www.' + new_product_url
    else:
        new_product_url = product_url
    try:
        html = urlopen(new_product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(new_product_url)

        # 상품 이름 정보 담기
        name = source.select('h3.tit-prd')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('td.price > div.tb-left')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'http://cdnok.makeshop.co.kr' + source.select('div.thumb > img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        model_detail_list = source.select('#model_image')[0].select('img')
        product_detail_list = source.select('#detail_image')[0].select('img')
        for i in range(len(model_detail_list)):
            url_list.append(model_detail_list[i]['src'])
        for i in range(len(product_detail_list)):
            url_list.append(product_detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


# NEW ADDED version 2 (2020.07.22)
def levlina_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://levlina.com' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def hyunslook_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://hyunslook.shop' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def armis_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea')[0].select('tr.xans-record-')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def secondrain_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def ladyl_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def lowear_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('li.name')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('li.inner')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://www.lowear.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def leehit_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            try:
                url_list.append('https:' + detail_list[i]['ec-data-src'])
            except:
                pass
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def cherrykoko_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('h2.prd_title')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('div.prd_data > em')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = source.select('div.thumb > img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.detail')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append(detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def mygon_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            try:
                url_list.append('https:' + detail_list[i]['ec-data-src'])
            except:
                pass
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def madejay_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://madejay.com' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def heigl_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://www.heigl.kr' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def hypnotic_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('li.name')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('li.price')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https://hypnotic.co.kr' + source.select('img.detail_image')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.prd-detail')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['src'].startswith('http:'):
                url_list.append(detail_list[i]['src'])
            else:
                pass
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def wvproject_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('li > strong')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('ul > li.sell')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https://wvproject.co.kr' + source.select('img.detail_image')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('center')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append(detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def peachpicnic_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.prdName')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.ThumbImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://peachpicnic.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def srable_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://www.srable.co.kr' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def oldmickey_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            try:
                url_list.append(detail_list[i]['ec-data-src'])
            except:
                #   url_list.append(detail_list[i]['src'])
                pass
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def weandme_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.infoArea > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def trendyapparel_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            try:
                url_list.append('https://trendy-apparel.co.kr' + detail_list[i]['ec-data-src'])
            except:
                pass
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def flymodel_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://flymodel.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def merryaround_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://merryaround.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def blackup_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h3')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://black-up.kr' + detail_list[i]['ec-data-src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def secondesecon_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://www.secondesecon.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def henique_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://henique.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def fromgirls_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.titleArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'http://fromgirls.co.kr' + source.select('div.thumb > img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.prd-detail')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append(detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def prostj_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.optCon > span')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('a.carousel-cell > img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['ec-data-src'].startswith('//prostj'):
                url_list.append('https:' + detail_list[i]['ec-data-src'])
            else:
                pass
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def perbit_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.ssname > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://perbit.co.kr' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def fromdayone_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('h2.info_name')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('http://www.fromdayone.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def ririnco_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https://ririnco.com' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def _09women_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('h3.tit-prd')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('span.price_focus')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = source.select('div.thumb')[0].select('img')[1]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.prd-detail')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append(detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def xexymix_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('h3.tit-prd')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('span.price')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https://www.xexymix.com' + source.select('div.thumb')[0].select('img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.image')[0].select('img')
        for i in range(len(detail_list)):
            url_list.append('https:' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def _98doci_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.headingArea > h2')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('img.BigImage')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.cont')[0].select('img')
        for i in range(len(detail_list)):
            try:
                url_list.append('https://98doci.com' + detail_list[i]['ec-data-src'])
            except:
                print("ERROR!")
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list


def page4_info_crawler(product_url):
    info_list = []
    if product_url.startswith('https://m.') or product_url.startswith('m.'):
        product_url = product_url.split('.')[1:]
        new_product_url = ''
        for i in range(len(product_url)):
            new_product_url = new_product_url + product_url[i] + '.'
        new_product_url = 'https://' + new_product_url
    else:
        new_product_url = product_url
    try:
        try:
            parse_product_url = new_product_url.split(':')[1]
            parse_product_url = parse.quote(parse_product_url)
            html = urlopen('https:' + parse_product_url)
            source = BeautifulSoup(html, 'html.parser')
        except:
            html = urlopen(new_product_url)
            source = BeautifulSoup(html, 'html.parser')

        # 쇼핑몰 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('div.mun-detail-desc')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'http://the-page4.com' + source.select('div.xans-product > img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.xans-product')[0].select('img')
        for i in range(len(detail_list)):
            if detail_list[i]['src'].startswith('/web'):
                url_list.append('http://the-page4.com' + detail_list[i]['src'])
            else:
                print('no')
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (
    ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError, ConnectionError, NewConnectionError,
    MaxRetryError):
        print("Connection Error")
    return info_list