from PIL import Image
from crawler.models import *
import colorgram
import colorsys

import numpy as np
import os
import tensorflow as tf
import cv2
from utils import ops as utils_ops
from utils import label_map_util

# Pre trained graph model PATH
MODEL_NAME = 'ssd_mobilenet_v1_1500_16_15000_people_no_handle_output'
PATH_TO_CKPT = os.path.join(MODEL_NAME, 'frozen_inference_graph.pb')
# Path to label map
PATH_TO_LABELS = os.path.join('training', 'object-detection.pbtxt')
NUM_CLASSES = 1

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
          # Get handles to input and output tensors
          ops = tf.get_default_graph().get_operations()
          all_tensor_names = {output.name for op in ops for output in op.outputs}
          tensor_dict = {}
          for key in [
              'num_detections', 'detection_boxes', 'detection_scores',
              'detection_classes', 'detection_masks'
          ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
              tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                  tensor_name)
          if 'detection_masks' in tensor_dict:
            # The following processing is only for single image
            detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
            detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
            # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
            real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
            detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
            detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
            detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                detection_masks, detection_boxes, image.shape[0], image.shape[1])
            detection_masks_reframed = tf.cast(
                tf.greater(detection_masks_reframed, 0.5), tf.uint8)
            # Follow the convention by adding back the batch dimension
            tensor_dict['detection_masks'] = tf.expand_dims(
                detection_masks_reframed, 0)
          image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

          # Run inference
          output_dict = sess.run(tensor_dict,
                                 feed_dict={image_tensor: np.expand_dims(image, 0)})

          # all outputs are float32 numpy arrays, so convert types as appropriate
          output_dict['num_detections'] = int(output_dict['num_detections'][0])
          output_dict['detection_classes'] = output_dict[
              'detection_classes'][0].astype(np.uint8)
          output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
          output_dict['detection_scores'] = output_dict['detection_scores'][0]
          if 'detection_masks' in output_dict:
            output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict


# Main function
def color_extraction():
    queryset = ColorTag.objects.filter(color=0).first()
    print(queryset)
    for obj in queryset:
        # image url 로 부터 이미지 가져오기
        response = requests.get(obj.colortab.product.bag_image.image_url)
        img = Image.open(BytesIO(response.content))
        # object-detection 으로 손잡이를 제외한 가방 찾기
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        image_np = load_image_into_numpy_array(img)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # Actual detection.
        output_dict = run_inference_for_single_image(image_np, detection_graph)
        top = output_dict['detection_boxes'][0][0]
        left = output_dict['detection_boxes'][0][1]
        bottom = output_dict['detection_boxes'][0][2]
        right = output_dict['detection_boxes'][0][3]
        # # color-extraction 을 위한 code
        cvt_img = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        cropped_img = cvt_img[top:bottom, left:right]
        # Extract 6 colors from an image.
        colors = colorgram.extract(cropped_img, 6)
        first_color = colors[0]
        rgb = first_color.rgb  # e.g. (255, 151, 210)
        proportion = first_color.proportion  # e.g. 0.34
        if proportion > 0.2:

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