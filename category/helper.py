import random
from copy import copy

from .models import Categories


shape_list = ['square', 'circle', 'bucket', 'half-circle', 'trapezoid', 'hobo', 'lying-cylinder']
handle_list = ['clutch', 'shoulder', 'tote', 'tote_shoulder', 'big_shoulder']
color_list = ['red', 'pink', 'orange', 'yellow', 'beige', 'green', 'blue', 'navy', 'purple', 'brown', 'black', 'white']
charm_list = ['tassel', 'leather', 'scarf', 'fur', 'none']
deco_list = ['bling', 'lock', 'lettering_printing', 'other', 'none']
pattern_list = ['leather', 'animal_print', 'quilt', 'monogram', 'floral', 'check', 'stripe', 'dot', 'lettering_printing', 'other', 'none']


def make_random_categories():
    shape = random_category(shape_list)
    handle = random_category(handle_list)
    color = random_category(color_list)
    charm = random_category(charm_list)
    deco = random_category(deco_list)
    pattern = random_category(pattern_list)
    return(shape, handle, color, charm, deco, pattern)


def random_category(sample_list):
    result = {}
    s_list = copy(sample_list)
    num = 1

    for i in range(3):
        temp = random.choice(s_list)
        random_n = random.triangular(0, num, num) #num 에 가까운 확률분포
        result[temp] = random_n
        n = s_list.index(temp)
        s_list.pop(n)
        num = num - random_n

    return result


def create_category(bag):
    shape, handle, color, charm, deco, pattern = make_random_categories()
    Categories.objects.get_or_create(bag_image=bag,
                                     defaults={
                                         'shape_result': shape,
                                         'handle_result': handle,
                                         'color_result': color,
                                         'charm_result': charm,
                                         'deco_result': deco,
                                         'pattern_result': pattern})