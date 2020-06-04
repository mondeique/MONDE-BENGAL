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
from celery import shared_task

# Create your views here.


class CrawlCreateAPIView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        data = self.request.data
        product_url = data['product_url']
        shopping_num, info_list = select_website(product_url)
        p = CrawlProduct.objects.create(shopping_mall=shopping_num, product_url=product_url,
                                        product_name=info_list[1], price=info_list[2], thumbnail_url=info_list[3],
                                        crawled_date=timezone.now(), is_valid=True)
        self.save_detail_image(self, p, info_list)
        CrawlColorTab.objects.create(product=p)
        CrawlSizeTab.objects.create(product=p)
        product_id = p.id
        return Response({"product_id" : product_id}, status=status.HTTP_201_CREATED)

    @shared_task
    def save_detail_image(self, product, info_list):
        for i in range(len(info_list[4])):
            CrawlDetailImage.objects.create(product=product, detail_url=info_list[4][i])



class CrawlRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CrawlProduct.objects.all()

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object(self)
        return Response({"product_id" : product.id}, status=status.HTTP_200_OK)

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
    elif product_url.find("commonunique") != -1:
        shopping_num = 15
        info_list = commonunique_info_crawler(product_url=product_url)
    elif product_url.find("baon") != -1:
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
    else:
        shopping_num = 22
        info_list = beginning_info_crawler(product_url=product_url)

    return shopping_num, info_list


def hotping_info_crawler(product_url):
    info_list = []
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

        # 상품 이름 정보 담기
        name = source.select('span.name')[0].get_text()
        info_list.append(name)

        # 가격 정보 추출하기
        price = source.select('#span_product_price_text')[0].get_text()
        info_list.append(price)

        # 이미지 thumbnail source html 정보 추출하기
        image_url = 'https:' + source.select('div.thumbnail')[0].select('img')[0]['src']
        info_list.append(image_url)

        # 이미지 detail source 정보 추출하기
        url_list = []
        detail_list = source.select('div.d_proimage')[0].select('img')
        for i in range(len(detail_list)):
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        product_url = product_url.split(':')[1]
        product_url = parse.quote(product_url)
        html = urlopen('https:' + product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        product_url = product_url.split(':')[1]
        product_url = parse.quote(product_url)
        html = urlopen('https:' + product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
            url_list.append('http:' + detail_list[i]['src'])
        info_list.append(url_list)

        # 서버 과부하를 위해 2s 간 멈춤
        time.sleep(2)
    except (ConnectionResetError, error.URLError, error.HTTPError, ConnectionRefusedError,
            ConnectionError, NewConnectionError, MaxRetryError):
        print("Connection Error")
    return info_list


def angtoo_info_crawler(product_url):
    info_list = []
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        product_url = product_url.split(':')[1]
        product_url = parse.quote(product_url)
        html = urlopen('https:' + product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append('https:' + product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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


def giftabox_info_crawler(product_url):
    info_list = []
    try:
        product_url = product_url.split(':')[1]
        product_url = parse.quote(product_url)
        html = urlopen('https:' + product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
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
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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
    info_list = []
    try:
        html = urlopen(product_url)
        source = BeautifulSoup(html, 'html.parser')

        # 가방 url 담기
        info_list.append(product_url)

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

