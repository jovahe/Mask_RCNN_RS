

import os,sys
import numpy as np
import glob
import json
import PIL.Image
from shapely.geometry import Polygon
from osgeo import ogr, gdal
gdal.UseExceptions()
from labelme import utils  # necessary


def get_file(file_dir, file_type=[".jpg",'.png', '.tif', '.tiff','.img','.pix']):
    im_type = ['.png']
    # print("进入get_file")
    if isinstance(file_type, str):
        im_type = file_type
    elif isinstance(file_type, list):
        im_type = file_type
    # print(im_type)
    # print("input_dir={}".format(file_dir))
    L = []
    if not os.path.isdir(file_dir):
        print("Error:input dir is not existed")
        return "", 0
    for root, dirs, files in os.walk(file_dir):
        # print("\nfiles")
        for file in files:
            if (str.lower(os.path.splitext(file)[1]) in im_type):
                L.append(os.path.join(root, file))
    num = len(L)
    if num == 0:
        L = ""
    return L, num

def get_img_from_shp(imgdir, shp_file):
    if not os.path.isdir(imgdir):
        if len(imgdir)==0:
            imgdir = os.path.dirname(shpfile)
            print("imdir is empty, now using the dir of shpfile:\n {}".format(imgdir))
        else:
            print("imgdir is illegal")
            return -1
    temp = ''
    str = os.path.split(shp_file)[1]
    str = str.split('.')[0]
    files, nb = get_file(imgdir)
    for file in files:
        if not str in file:
            continue
        else:
            temp = file
    # if len(temp.strip())==0:
    #     # raise FError('No file in diretotry')
    #     return None
    else:
        return temp


class shp2coco(object):
    def __init__(self, shpfile=[], save_json_path='./new.json', imgdir = ''):
        '''
        :param labelme_json: 所有labelme的json文件路径组成的列表
        :param save_json_path: json保存位置
        '''
        self.shpfile = shpfile
        self.imgdir = imgdir
        self.save_json_path = save_json_path
        self.images = []
        # self.categories=[]
        # self.categories = [{'supercategory': 'column', 'id': 1, 'name': 'column'}, {'supercategory': 'box', 'id': 2, 'name': 'box'}, {'supercategory': 'fruit', 'id': 3, 'name': 'fruit'}, {'supercategory': 'package', 'id': 4, 'name': 'package'}]
        self.categories = [{'supercategory': 'A', 'id': 1, 'name': 'building'}]

        self.annotations = []
        # self.data_coco = {}
        self.label = []
        self.annID = 1
        self.height = 0
        self.width = 0

        self.save_json()

    def data_transfer(self):
        for num, shp_file in enumerate(self.shpfile):

            # get image info

            ret =0
            ret = get_img_from_shp(self.imgdir, shp_file)
            if isinstance(ret,int) or len(ret) ==0:
                print("Warning: can not find the corresponding image:\n {}".format(shp_file))
                continue
            print("image:", ret)

            self.images.append(self.image(ret, num))
            print(self.images)


            # 打开矢量图层
            gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
            gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
            fp = ogr.Open(shp_file)

            shp_lyr = fp.GetLayer(0)
            numFeatures = shp_lyr.GetFeatureCount()

            # 循环每个要素属性
            for i in range(numFeatures):
                feature = shp_lyr.GetNextFeature()
                # 获取字段“id”的属性

                try:
                    label = feature.GetField('label')
                except:
                    print("can not get the label")
                    label = 'ship'
                print("the {}th feature is :",i+1, label)


                if label == None:
                    print("Warning: feature is background")
                    continue

                # 获取空间属性
                geometry = feature.GetGeometryRef()

                feat= geometry.GetGeometryRef(0)

                points =[]
                for i in range(feat.GetPointCount()-1):
                    x = abs(feat.GetX(point=i))
                    y = abs(feat.GetY(point=i))
                    points.append([x,y])

                print(points)
                self.annotations.append(self.annotation(points, label, num))
                self.annID += 1

        print(self.categories)

    def image(self, file, num):
        image = {}
        # img = utils.img_b64_to_arr(data['imageData'])  # 解析原图片数据
        # img=io.imread(data['imagePath']) # 通过图片路径打开图片
        # img = cv2.imread(data['imagePath'], 0)
        # height, width = img.shape[:2]
        try:
            dataset = gdal.Open(file, gdal.GF_Read)
        except:
            print("Warning: can not open file:\n {}".format(file))
            return -1
        height = dataset.RasterYSize
        width = dataset.RasterXSize

        del dataset

        img = None
        image['height'] = height
        image['width'] = width
        image['id'] = num + 1
        image['file_name'] = file.split('/')[-1]

        self.height = height
        self.width = width

        return image


    def annotation(self, points, label, num):
        annotation = {}
        annotation['segmentation'] = [list(np.asarray(points).flatten())]
        poly = Polygon(points)
        area_ = round(poly.area, 6)
        annotation['area'] = area_
        annotation['iscrowd'] = 0
        annotation['image_id'] = num + 1
        # annotation['bbox'] = str(self.getbbox(points)) # 使用list保存json文件时报错（不知道为什么）
        # list(map(int,a[1:-1].split(','))) a=annotation['bbox'] 使用该方式转成list
        annotation['bbox'] = list(map(float, self.getbbox(points)))

        annotation['category_id'] = self.getcatid(label)
        # print(label)
        # annotation['category_id'] = len(self.label) + 1
        # print(self.getcatid(label))
        annotation['id'] = self.annID
        return annotation

    def getcatid(self, label):
        for categorie in self.categories:
            if label == categorie['name']:
                return categorie['id']
        return -1

    def getbbox(self, points):
        # img = np.zeros([self.height,self.width],np.uint8)
        # cv2.polylines(img, [np.asarray(points)], True, 1, lineType=cv2.LINE_AA)  # 画边界线
        # cv2.fillPoly(img, [np.asarray(points)], 1)  # 画多边形 内部像素值为1
        polygons = points
        mask = self.polygons_to_mask([self.height, self.width], polygons)
        return self.mask2box(mask)

    def mask2box(self, mask):
        '''从mask反算出其边框
        mask：[h,w]  0、1组成的图片
        1对应对象，只需计算1对应的行列号（左上角行列号，右下角行列号，就可以算出其边框）
        '''
        # np.where(mask==1)
        index = np.argwhere(mask == 1)
        rows = index[:, 0]
        clos = index[:, 1]
        # 解析左上角行列号
        left_top_r = np.min(rows)  # y
        left_top_c = np.min(clos)  # x

        # 解析右下角行列号
        right_bottom_r = np.max(rows)
        right_bottom_c = np.max(clos)

        # return [(left_top_r,left_top_c),(right_bottom_r,right_bottom_c)]
        # return [(left_top_c, left_top_r), (right_bottom_c, right_bottom_r)]
        # return [left_top_c, left_top_r, right_bottom_c, right_bottom_r]  # [x1,y1,x2,y2]
        return [left_top_c, left_top_r, right_bottom_c - left_top_c,
                right_bottom_r - left_top_r]  # [x1,y1,w,h] 对应COCO的bbox格式

    def polygons_to_mask(self, img_shape, polygons):
        mask = np.zeros(img_shape, dtype=np.uint8)
        mask = PIL.Image.fromarray(mask)
        xy = list(map(tuple, polygons))
        PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
        mask = np.array(mask, dtype=bool)
        return mask

    def data2coco(self):
        data_coco = {}
        data_coco['images'] = self.images
        data_coco['categories'] = self.categories
        data_coco['annotations'] = self.annotations
        return data_coco

    def save_json(self):
        self.data_transfer()
        self.data_coco = self.data2coco()
        # 保存json文件
        json.dump(self.data_coco, open(self.save_json_path, 'w'), indent=4)  # indent=4 更加美观显示



if __name__=='__main__':

    shp_path = "/home/omnisky/PycharmProjects/data/maskRcnn/cocotest/whubuilding/ori_from_win10/test/label_pixel_unit/"
    image_path = "/home/omnisky/PycharmProjects/data/maskRcnn/cocotest/whubuilding/test/"
    shpfile = glob.glob(shp_path+'/*.shp')

    shp2coco(shpfile,
             '/home/omnisky/PycharmProjects/data/maskRcnn/cocotest/whubuilding/annotations/instances_test.json',
             image_path)

