import os
import sys
import skimage.io
import random
from samples.coco import coco
from mrcnn import visualize
from mrcnn import model as modellib
from my.tools import geo_convert as geo
from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
 #Root directory of the project
ROOT_DIR = os.path.abspath("../")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
from samples.coco import coco

#%matplotlib inline

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

# Local path to trained weights file
# COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
COCO_MODEL_PATH='/home/omnisky/PycharmProjects/Mask_RCNN/logs/coco20200924T1150/mask_rcnn_coco_0120.h5'
# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)

# Directory of images to run detection on
IMAGE_DIR = os.path.join(ROOT_DIR, "images")

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    NUM_CLASSES = 1 + 1

config = InferenceConfig()
config.display()

# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)

# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
# class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
#                'bus', 'train', 'truck', 'boat', 'traffic light',
#                'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
#                'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
#                'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
#                'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
#                'kite', 'baseball bat', 'baseball glove', 'skateboard',
#                'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
#                'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
#                'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
#                'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
#                'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
#                'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
#                'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
#                'teddy bear', 'hair drier', 'toothbrush']
class_names = ['BG', 'building']

# Load a random image from the images folder
# file_names = next(os.walk(IMAGE_DIR))[2]
# image = skimage.io.imread(os.path.join(IMAGE_DIR, random.choice(file_names)))
#
#
#
# # Run detection
# results = model.detect([image], verbose=1)

from my.shp2COCO import get_file

if __name__=='__main__':

    data_dir = '/home/omnisky/PycharmProjects/Mask_RCNN/images/1/'
    files, _ = get_file(data_dir)

    for file in files:
        # file_name = '/home/omnisky/PycharmProjects/data/maskRcnn/mytest/rcnnpredicted/3800883468_12af3c0b50_z.jpg'  # 输入的tiff图像
        test_image = skimage.io.imread(file)

        predictions = model.detect([test_image] * config.BATCH_SIZE,
                                   verbose=1)
        p = predictions[0]

        # 存储为shapefile
        absname = os.path.basename(file)
        absname = absname.split('.')[0]
        masks = p['masks']

        print("value:{}".format(np.unique(masks[:,:,0])))
        plt.imshow(masks[:,:,0])
        plt.show()

        save_name = data_dir+absname+'.shp'  # 输出路径, shp是反的?
        data_tiff = gdal.Open(file)
        ref = data_tiff.GetGeoTransform()
        geom = geo.create_geom_from_rcnnmask(masks, reference=ref)
        geo.convert_geom_to_shp(geom, outputfile_name=save_name)

        # 图像显示
        visualize.display_instances(test_image, p['rois'], p['masks'], p['class_ids'],
                                    class_names, p['scores'])