import requests
from django.db import models
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from crawler.tools import get_image_filename


class Product(models.Model):
    LUZZIBAG = 1
    PAU = 2
    JADE = 3
    BANAMALL = 4
    BEGINNING = 5
    BNBURDE = 6
    WCONCEPT = 7
    GABANGPOP = 8
    BAGSHOES = 9
    MCLANEE = 10
    MJADE = 11
    PINKBAG = 12
    WHOSBAG = 13
    SITE_CHOICES = (
        (LUZZIBAG, 'luzzibag'),
        (PAU, 'paris and you'),
        (JADE, 'jade'),
        (BANAMALL, 'banabana mall'),
        (BEGINNING, 'beginning'),
        (BNBURDE, 'bnburde'),
        (WCONCEPT, 'wconcept'),
        (GABANGPOP, 'gabangpop'),
        (BAGSHOES, 'bagshoes'),
        (MCLANEE, 'mclanee'),
        (MJADE, 'mjade'),
        (PINKBAG, 'pinkbag'),
        (WHOSBAG, 'whosbag'),
    )
    shopping_mall = models.IntegerField(choices=SITE_CHOICES, help_text='crawling 된 bag 의 homepage')
    is_banned = models.BooleanField(default=False, help_text='best에 가방 외의 것들이 들어갈 수 있기 때문에 생성된 필드')
    # image_url = models.URLField(help_text='가방 이미지의 html image source')
    product_name = models.CharField(null=True, max_length=100)
    bag_url = models.URLField(help_text='한 상품에 대한 url')
    is_best = models.BooleanField(default=False)
    price = models.CharField(max_length=50)
    crawled_date = models.DateTimeField(null=True, blank=True)


class BagImage(models.Model):
    product = models.ForeignKey(Product, related_name='bag_images', null=True, on_delete=models.SET_NULL) #쇼핑몰에서 사라져도 data는 저장되게 하기 위해
    image_url = models.URLField(help_text='가방 이미지의 html image source')
    bag_image = models.ImageField(upload_to='crawled-image', blank=True)
    order = models.PositiveIntegerField(default=1)

    def get_image_extension(self):
        return 'jpeg'

    def save(self, *args, **kwargs):
        super(BagImage, self).save(*args, **kwargs)
        # TODO : FIX ME
        self._save_image()

    def _save_image(self):
        # TODO : crop 말고 저장
        from PIL import Image
        resp = requests.get(self.image_url, headers={'User-Agent': 'Mozilla/5.0'})
        print('request ok')
        # image = Image.open(BytesIO(resp.content))
        byteImgIO = BytesIO()
        byteImg = Image.open(BytesIO(resp.content))
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
        crop_file = InMemoryUploadedFile(crop_io, None, get_image_filename(self.bag_image), 'image/jpeg', len(crop_io.getvalue()), None)
        print('memory upload ok')
        self.bag_image.save(get_image_filename(self.bag_image), crop_file, save=False)
        # To avoid recursive save, call super.save
        super(BagImage, self).save()


class ColorTab(models.Model):
    product = models.ForeignKey(Product, related_name='color_tabs', on_delete=models.CASCADE)
    is_mono = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=True)
    colors = models.CharField(max_length=50)


class ColorTag(models.Model):
    DUMP = 0
    RED = 1
    PINK = 2
    ORANGE = 3
    YELLOW = 4
    BEIGE = 5
    GREEN = 6
    BLUE = 7
    NAVY = 8
    PURPLE = 9
    BROWN = 10
    BLACK = 11
    WHITE = 12
    GRAY = 13
    MULTI = 99
    COLOR_CHOICES = (
        (RED, 'red'),
        (PINK, 'pink'),
        (ORANGE, 'orange'),
        (YELLOW, 'yellow'),
        (BEIGE, 'beige'),
        (GREEN, 'green'),
        (BLUE, 'blue'),
        (NAVY, 'navy'),
        (PURPLE, 'purple'),
        (BROWN, 'brown'),
        (BLACK, 'black'),
        (WHITE, 'white'),
        (GRAY, 'gray'),
        (MULTI, 'multi')
    )
    colortab = models.ForeignKey(ColorTab, related_name='color_tags', on_delete=models.CASCADE)
    color = models.IntegerField(choices=COLOR_CHOICES)





