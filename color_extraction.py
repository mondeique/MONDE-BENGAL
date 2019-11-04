from PIL import Image
from crawler.models import *
import colorgram
import colorsys


def color_extraction():
    queryset = ColorTag.objects.filter(color=0)
    for obj in queryset:
        response = requests.get(obj.colortab.product.bag_image.image_url)
        img = Image.open(BytesIO(response.content))
        # TODO : object-detection 붙이기
        # Extract 6 colors from an image.
        colors = colorgram.extract(img, 6)
        first_color = colors[0]
        rgb = first_color.rgb  # e.g. (255, 151, 210)
        proportion = first_color.proportion  # e.g. 0.34
        if proportion > 0.3:

            # We have Red/Pink/Orange/Yellow/Beige/Green/Blue/Navy/Purple/Brown/Black/White/Gray
            # H를 먼저 정한 뒤 S와 V를 조절하면서 색을 찾아나가도록 하자.
            # Beige와 Brown을 제외한 색은 Hue에 의해서만 결정된다고 가정하자.
            # 추가로 수정될 경우 그 때 수정하자.

            Hue = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)[0]
            Saturation = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)[1]
            Value = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)[2]

            Hue = Hue * 360
            Saturation = Saturation * 100
            Value = Value * 100

            if 0 <= Hue <= 15 and 345 <= Hue <= 360 and Saturation > 15 and Value > 30:
                result = 1
            elif 315 <= Hue <= 345 and Saturation > 15 and Value > 30:
                result = 2
            elif 15 < Hue < 40 and Saturation > 45 and Value > 80:
                result = 3
            elif 40 <= Hue < 70 and Saturation > 15 and Value > 30:
                result = 4
            elif 15 < Hue < 40 and 5 < Saturation < 45 and Value > 70:
                result = 5
            elif 70 <= Hue < 170 and Saturation > 15 and Value > 30:
                result = 6
            elif 170 <= Hue < 265 and Saturation > 15 and Value > 30:
                result = 7
            elif 170 <= Hue < 265 and Saturation > 30 and 30 < Value < 40:
                result = 8
            elif 265 <= Hue < 315 and Saturation > 15 and Value > 30:
                result = 9
            elif 15 < Hue < 40 and Saturation > 50 and 30 < Value < 80:
                result = 10
            elif Saturation < 15 and Value < 20:
                result = 11
            elif Saturation <= 2 and Value >= 90:
                result = 12
            else:
                result = 13
            p = ColorTag.objects.get(pk=obj.id)
            p.color = result
            p.save()
        else:
            result = 99
            p = ColorTag.objects.get(pk=obj.id)
            p.color = result
            p.save()