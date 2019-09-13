import jsonfield
from django.db import models

from crawler.models import Product, BagImage

PRECISION = 4



class Categories(models.Model):
    bag_image = models.OneToOneField(BagImage, related_name="categories", null=True, on_delete=models.CASCADE)
    # accuracy = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    shape_result = jsonfield.JSONField(default=dict) # {'bucket':0.8832, 'rectangle':0.11, 'circle':0.01}
    handle_result = jsonfield.JSONField(default=dict)
    #TODO : how to search multi colors?
    color_result = jsonfield.JSONField(default=dict)
    # 멀티 컬러인 경우
    charm_result = jsonfield.JSONField(default=dict)
    deco_result = jsonfield.JSONField(default=dict)
    pattern_result = jsonfield.JSONField(default=dict)