import jsonfield
from django.db import models

# from crawler.models import Product, BagImage

PRECISION = 4



# class Categories(models.Model):
#     bag_image = models.OneToOneField(BagImage, related_name="categories", on_delete=models.CASCADE)
#     # accuracy = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
#     shape_result = jsonfield.JSONField(default=dict) # {'bucket':0.8832, 'rectangle':0.11, 'circle':0.01}
#     handle_result = jsonfield.JSONField(default=dict)
#     #TODO : how to search multi colors?
#     color_result = jsonfield.JSONField(default=dict)
#     # 멀티 컬러인 경우 트레이닝 시키지 않고 결과 확인했을떄 red 0.3, blue 0.4, brown 0.2이면 multi color로. 검색시에는 multi color선택했을때는 multi만, 그냥 red검색시에는 red + multi
#     charm_result = jsonfield.JSONField(default=dict)
#     deco_result = jsonfield.JSONField(default=dict)
#     pattern_result = jsonfield.JSONField(default=dict)