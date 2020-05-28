import requests
from django.db import models
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from crawler.tools import get_image_filename


class Product(models.Model):
    HOTPING = 1
    _66GIRLS = 2
    GGSING = 3
    MIXXMIX = 4
    STYLENANDA = 5
    IMVELY = 6
    SLOWAND = 7
    WITHYOON = 8
    CREAMCHEESE = 9
    SLOWBERRY = 10
    MOODLOVEROOM = 11
    LOVEANDPOP = 12
    ANGTOO = 13
    UNIQUEON = 14
    COMMONUNIQUE = 15
    BAON = 16
    MAYBINS = 17
    GIFTABOX = 18
    MAYBEBABY = 19
    VINVLE = 20
    ATTRANGS = 21
    BEGINNING = 22
    SITE_CHOICES = (
        (HOTPING, ('핫핑')),
        (_66GIRLS, ('66걸즈')),
        (GGSING, ('고고싱')),
        (MIXXMIX, ('믹스액스믹스')),
        (STYLENANDA, ('스타일난다')),
        (IMVELY, ('임블리')),
        (SLOWAND, ('슬로우앤드')),
        (WITHYOON, ('위드윤')),
        (CREAMCHEESE, ('크림치즈마켓')),
        (SLOWBERRY, ('슬로우베리')),
        (MOODLOVEROOM, ('무드러브룸')),
        (LOVEANDPOP, ('러브앤드팝')),
        (ANGTOO, ('앙투')),
        (UNIQUEON, ('유니크온')),
        (COMMONUNIQUE, ('커먼유니크')),
        (BAON, ('바온')),
        (MAYBINS, ('메이빈스')),
        (GIFTABOX, ('기프트박스')),
        (MAYBEBABY, ('메이비베이비')),
        (VINVLE, ('빈블')),
        (ATTRANGS, ('아뜨랑스')),
        (BEGINNING, ('프롬비기닝'))
    )
    shopping_mall = models.IntegerField(choices=SITE_CHOICES, help_text='crawling website number')
    # is_banned = models.BooleanField(default=False, help_text='best에 가방 외의 것들이 들어갈 수 있기 때문에 생성된 필드')
    thumbnail_url = models.URLField(help_text='thumbnail html image source')
    thumbnail_image = models.ImageField(upload_to='thumbnail-image', blank=True)
    size_image = models.ImageField(upload_to='size-image', blank=True, help_text='captured size image')
    product_name = models.CharField(null=True, max_length=100)
    product_url = models.URLField(help_text='한 상품에 대한 url')
    # is_best = models.BooleanField(default=False)
    price = models.CharField(max_length=50)
    crawled_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_valid = models.BooleanField(default=True, help_text='만료된 웹 페이지의 경우 False로 변경됨')


class DetailImage(models.Model):
    # Product 하나당 상세이미지 여러개 -> Foreign Key 연결
    product = models.ForeignKey(Product, related_name='detail_image', null=True, on_delete=models.CASCADE)
    detail_url = models.URLField(help_text='detail html image source')
    detail_image = models.ImageField(upload_to='detail-image', blank=True)

    def get_image_extension(self):
        return 'jpeg'

    def save(self, *args, **kwargs):
        super(DetailImage, self).save(*args, **kwargs)
        # TODO : FIX ME
        self._save_image()

    def _save_image(self):
        # TODO : crop 말고 저장
        from PIL import Image
        resp = requests.get(self.detail_url, headers={'User-Agent': 'Mozilla/5.0'})
        print('request ok')
        # image = Image.open(BytesIO(resp.content))
        byteImgIO = BytesIO()
        try:
            byteImg = Image.open(BytesIO(resp.content))
            byteImg = byteImg.convert("RGB")
            byteImg.save(byteImgIO, "JPEG")
            byteImgIO.seek(0)
            byteImg = byteImgIO.read()
            dataBytesIO = BytesIO(byteImg)
            image = Image.open(dataBytesIO)
            print('image open ok')
            width, height = image.size
            left = width * 0.01
            top = height * 0.01
            right = width * 0.99
            bottom = height * 0.99
            crop_data = image.crop((int(left), int(top), int(right), int(bottom)))
            # http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
            crop_io = BytesIO()
            crop_data.save(crop_io, format=self.get_image_extension())
            print('crop data save ok')
            crop_file = InMemoryUploadedFile(crop_io, None, get_image_filename(self.detail_image), 'image/jpeg', len(crop_io.getvalue()), None)
            print('memory upload ok')
            self.detail_image.save(get_image_filename(self.detail_image), crop_file, save=False)
            # To avoid recursive save, call super.save
            super(DetailImage, self).save()
        except OSError:
            print("OSError")


class ColorTab(models.Model):
    product = models.ForeignKey(Product, related_name='color_tabs', on_delete=models.CASCADE)
    is_mono = models.BooleanField(default=False)
    colors = models.CharField(blank=True, max_length=50)


class SizeTab(models.Model):
    DUMP = 0
    XS = 1
    S = 2
    M = 3
    L = 4
    XL = 5
    FREE = 6
    SIZE_CHOICES = (
        (DUMP, 'not selected'),
        (XS, 'x small'),
        (S, 'small'),
        (M, 'medium'),
        (L, 'large'),
        (XL, 'x large'),
        (FREE, 'free')
    )
    product = models.ForeignKey(Product, related_name='size_tabs', on_delete=models.CASCADE)
    size = models.IntegerField(default=0, choices=SIZE_CHOICES, help_text='crawled product size')


# class ColorTag(models.Model):
#     DUMP = 0
#     RED = 1
#     PINK = 2
#     ORANGE = 3
#     YELLOW = 4
#     BEIGE = 5
#     GREEN = 6
#     BLUE = 7
#     NAVY = 8
#     PURPLE = 9
#     BROWN = 10
#     BLACK = 11
#     WHITE = 12
#     GRAY = 13
#     MULTI = 99
#     COLOR_CHOICES = (
#         (RED, 'red'),
#         (PINK, 'pink'),
#         (ORANGE, 'orange'),
#         (YELLOW, 'yellow'),
#         (BEIGE, 'beige'),
#         (GREEN, 'green'),
#         (BLUE, 'blue'),
#         (NAVY, 'navy'),
#         (PURPLE, 'purple'),
#         (BROWN, 'brown'),
#         (BLACK, 'black'),
#         (WHITE, 'white'),
#         (GRAY, 'gray'),
#         (MULTI, 'multi')
#     )
#     colortab = models.ForeignKey(ColorTab, related_name='color_tags', on_delete=models.CASCADE)
#     color = models.IntegerField(choices=COLOR_CHOICES)
#     color_review = models.BooleanField(default=False)





