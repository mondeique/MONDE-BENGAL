import random
import string


def get_image_filename(image):
    _First = '_1'

    if image:
        whole_name = image.name
        jpg_name = whole_name.split('/')[1]
        prev_name = jpg_name.split('.')[0]
        name = prev_name.split('_')[0]
        name_order = int(prev_name.split('_')[1])
        next_order = name_order + 1
        rename = name + '_' + str(next_order) + '.jpg'
        print('renamed!')
        return rename
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + \
           random.choice(string.ascii_uppercase) + _First + '.jpg'