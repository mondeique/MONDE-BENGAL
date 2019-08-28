from django.db import models


class Product(models.Model):
    LUZZIBAG = 1
    PAU = 2
    JADE = 3
    BANAMALL = 4
    BEGINNING = 5
    BNBURDE = 6
    COMING = 7
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
        (COMING, 'comingbag'),
        (GABANGPOP, 'gabangpop'),
        (BAGSHOES, 'bagshoes'),
        (MCLANEE, 'mclanee'),
        (MJADE, 'mjade'),
        (PINKBAG, 'pinkbag'),
        (WHOSBAG, 'whosbag'),
    )
    shopping_mall = models.IntegerField(choices=SITE_CHOICES, help_text='crawling 된 bag 의 homepage')
    image_url = models.URLField(help_text='가방 이미지의 html image source')
    product_name = models.CharField(null=True, max_length=100)
    bag_url = models.URLField(help_text='한 상품에 대한 url')
    is_best = models.BooleanField(default=False)
    price = models.CharField(max_length=50)
    crawled_date = models.DateTimeField(null=True, blank=True)


class BagImage(models.Model):
    product = models.ForeignKey(Product, related_name='bag_images', on_delete=models.CASCADE)
    # TODO 이름 짓기
    bag_image = models.ImageField(upload_to='')
    order = models.PositiveIntegerField(default=1)


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





