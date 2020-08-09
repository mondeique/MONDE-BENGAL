import requests
from django.db import models
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from crawler.tools import get_image_filename
from PIL import Image
import sys
import os


class CrawlProduct(models.Model):
    DUMP = 0
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
    # New added shopping mall
    LEVLINA = 23
    HYUNSLOOK = 24
    ARMIS = 25
    SECONDRAIN = 26
    LADYL = 27
    LOWEAR = 28
    LEEHIT = 29
    CHERRYKOKO = 30
    MYGON = 31
    MADEJAY = 32
    HEIGL = 33
    HYPNOTIC = 34
    WVPROJECT = 35
    PEACHPICNIC = 36
    SRABLE = 37
    OLDMICKEY = 38
    # 2020.07.29 daniel
    WEANDME = 39
    TRENDY = 40
    FLYMODEL = 41
    MERRYAROUND = 42
    BLACKUP = 43
    SECONDDESECON = 44
    HENIQUE = 45
    FROMGIRLS = 46
    PROSTJ = 47
    PERBIT = 48
    FROMDAYONE = 49
    RIRINCO = 50
    _09WOMEN = 51
    XEXYMIX = 52
    _98DOCI = 53
    PAGE4 = 54
    BENITO = 55
    MINSSHOP = 56
    ANDAR = 57
    LIKEYOU = 58
    DAILYJOU = 59
    _30me = 60


    SITE_CHOICES = (
        (DUMP, ('추가되지 않은 쇼핑몰')),
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
        (BEGINNING, ('프롬비기닝')),
        (LEVLINA, ('레브리나')),
        (HYUNSLOOK, ('현스룩')),
        (ARMIS, ('아르미스')),
        (SECONDRAIN, ('세컨드레인')),
        (LADYL, ('레이디엘')),
        (LOWEAR, ('로웨어')),
        (LEEHIT, ('리히트')),
        (CHERRYKOKO, ('체리코코')),
        (MYGON, ('마이곤')),
        (MADEJAY, ('메이드제이')),
        (HEIGL, ('헤이지엘')),
        (HYPNOTIC, ('히포노틱')),
        (WVPROJECT, ('WV프로젝트')),
        (PEACHPICNIC, ('피치피크닉')),
        (SRABLE, ('에스레이블')),
        (OLDMICKEY, ('올드미키')),
        (WEANDME, ('위앤미')),
        (TRENDY, ('트렌디어필')),
        (FLYMODEL, ('플라이모델')),
        (MERRYAROUND, ('메리어라운드')),
        (BLACKUP, ('블랙')),
        (SECONDDESECON, ('세컨드데세컨')),
        (HENIQUE, ('헤니크')),
        (FROMGIRLS, ('프롬걸스')),
        (PROSTJ, ('프로스트제이')),
        (PERBIT, ('퍼비트')),
        (FROMDAYONE, ('프롬데이원')),
        (RIRINCO, ('리린코')),
        (_09WOMEN, ('09우먼')),
        (XEXYMIX, ('엑시믹스')),
        (_98DOCI, ('98도시')),
        (PAGE4, ('페이지포')),
        (BENITO, ('비니토')),
        (MINSSHOP, ('민스샵')),
        (ANDAR, ('앤달')),
        (LIKEYOU, ('라이크유')),
        (DAILYJOU, ('데일리쥬')),
        (_30me, ('써리미'))
    )

    # TODO : bucket upload-to 조정
    shopping_mall = models.IntegerField(choices=SITE_CHOICES, help_text='crawling website number')
    # is_banned = models.BooleanField(default=False, help_text='best에 가방 외의 것들이 들어갈 수 있기 때문에 생성된 필드')
    thumbnail_url = models.CharField(help_text='thumbnail html image source', max_length=500)
    thumbnail_image = models.ImageField(upload_to='thumbnail-image', blank=True)
    size_image = models.ImageField(upload_to='size-image', null=True, help_text='captured size image')
    product_name = models.CharField(null=True, max_length=100)
    product_url = models.CharField(help_text='한 상품에 대한 url', max_length=500)
    # is_best = models.BooleanField(default=False)
    price = models.CharField(max_length=50)
    crawled_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_valid = models.BooleanField(default=True, help_text='만료된 웹 페이지의 경우 False로 변경됨')

    def get_image_extension(self):
        return 'jpeg'

    def save(self, *args, **kwargs):
        super(CrawlProduct, self).save(*args, **kwargs)
        self._save_image()

    # GIF TO JPG converter
    def iter_frames(image):
        try:
            i = 0
            image.seek(i)
            imframe = image.copy()
            yield imframe
        except EOFError:
            pass

    def _save_image(self):
        # TODO : crop 말고 저장
        from PIL import Image
        try:
            resp = requests.get(self.thumbnail_url, headers={'User-Agent': 'Mozilla/5.0'})
            print('request ok')
            # gif to jpg converter
            # if self.thumbnail_url.find('.gif'):
            #     try:
            #         # curl 요청
            #         os.system("curl " + self.thumbnail_url + " > test.gif")
            #
            #         im = Image.open('./test.gif')
            #         for i, frame in enumerate(self.iter_frames(im)):
            #             frame.save('test%d.png' % i, **frame.info)
            #
            #         image = Image.open('./test0.png')
            #         width, height = image.size
            #         left = width * 0.01
            #         top = height * 0.01
            #         right = width * 0.99
            #         bottom = height * 0.99
            #         crop_data = image.crop((int(left), int(top), int(right), int(bottom)))
            #         # http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
            #         crop_io = BytesIO()
            #         crop_data.save(crop_io, format=self.get_image_extension())
            #         print('crop data save ok')
            #         crop_file = InMemoryUploadedFile(crop_io, None, get_image_filename(self.thumbnail_image), 'image/jpeg',
            #                                          len(crop_io.getvalue()), None)
            #         print('memory upload ok')
            #
            #         os.remove('./test.gif')
            #         os.remove('./test0.png')
            #
            #         self.thumbnail_image.save(get_image_filename(self.thumbnail_image), crop_file, save=False)
            #         # To avoid recursive save, call super.save
            #         super(CrawlProduct, self).save()
            #     except OSError:
            #         print("OSERROR")
            # else:
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
                crop_file = InMemoryUploadedFile(crop_io, None, get_image_filename(self.thumbnail_image), 'image/jpeg', len(crop_io.getvalue()), None)
                print('memory upload ok')
                self.thumbnail_image.save(get_image_filename(self.thumbnail_image), crop_file, save=False)
                # To avoid recursive save, call super.save
                super(CrawlProduct, self).save()
            except OSError:
                print("OSError")
        except:
            print("REQUEST ERROR")


class CrawlDetailImage(models.Model):
    # Product 하나당 상세이미지 여러개 -> Foreign Key 연결
    product = models.ForeignKey(CrawlProduct, related_name='detail_images', null=True, on_delete=models.CASCADE)
    detail_url = models.URLField(help_text='detail html image source')
    detail_image = models.ImageField(upload_to='detail-image', blank=True, null=True)
    detail_image_crop = models.ImageField(upload_to='detail-image-crop', blank=True, null=True)

    def get_image_extension(self):
        return 'jpeg'

    def save(self, *args, **kwargs):
        super(CrawlDetailImage, self).save(*args, **kwargs)
        # TODO : FIX ME
        self._save_image()

    def _save_image(self):
        # TODO : crop 말고 저장
        from PIL import Image
        try:
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
                if height > 4305:
                    crop_bottom = 4305
                    crop_data = image.crop((int(left), int(top), int(right), int(crop_bottom)))
                    # http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
                    crop_io = BytesIO()
                    crop_data.save(crop_io, format=self.get_image_extension())
                    print('4305 crop data save ok')
                    crop_file = InMemoryUploadedFile(crop_io, None, get_image_filename(self.detail_image_crop), 'image/jpeg',
                                                     len(crop_io.getvalue()), None)
                    print('4305 memory upload ok')
                    self.detail_image_crop.save(get_image_filename(self.detail_image_crop), crop_file, save=False)
                    # To avoid recursive save, call super.save
                    # super(CrawlDetailImage, self).save()
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
                super(CrawlDetailImage, self).save()
            except OSError:
                print("OSError")
        except:
            print("REQUEST ERROR")



class CrawlColorTab(models.Model):
    product = models.ForeignKey(CrawlProduct, related_name='color_tabs', on_delete=models.CASCADE)
    is_mono = models.BooleanField(default=False)
    colors = models.CharField(blank=True, max_length=50)


class CrawlSizeTab(models.Model):
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
    product = models.ForeignKey(CrawlProduct, related_name='size_tabs', on_delete=models.CASCADE)
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





