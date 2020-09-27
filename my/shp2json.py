# -*- coding: utf-8 -*-
from osgeo import ogr
import gdal
import sys
import os
import fire

def ChangeToJson(vector, output):
    print("Starting........")
    #打开矢量图层
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
    shp_ds = ogr.Open(vector)
    shp_lyr = shp_ds.GetLayer(0)
    numFeatures = shp_lyr.GetFeatureCount()
    print("Features number:{}".format(numFeatures))

    # 获取范围
    extent = shp_lyr.GetExtent()
    print("Extent:", extent)
    print("UL:", extent[0], extent[3])
    print("LR:", extent[1], extent[2])

    # 循环每个要素属性
    for i in range(numFeatures):
        feature = shp_lyr.GetNextFeature()
        # 获取字段“id”的属性
        # id = feature.GetField('type')
        # 获取空间属性
        # print(id)
        geometry = feature.GetGeometryRef()
        # x = geometry.GetX()
        polygonextent = geometry.GetEnvelope()
        print(geometry.GetEnvelope())
        # print(y)

        # y = geometry.GetY()
        print("UL:", polygonextent[0], polygonextent[3])
        print("LR:", polygonextent[1], polygonextent[2])
        print("segmentation:", geometry)



    # # 创建结果Geojson
    # baseName = os.path.basename(output)
    # out_driver = ogr.GetDriverByName('GeoJSON')
    # out_ds = out_driver.CreateDataSource(output)
    # if out_ds.GetLayer(baseName):
    #     out_ds.DeleteLayer(baseName)
    # out_lyr = out_ds.CreateLayer(baseName, shp_lyr.GetSpatialRef())
    # out_lyr.CreateFields(shp_lyr.schema)
    # out_feat = ogr.Feature(out_lyr.GetLayerDefn())
    #
    # #生成结果文件
    # for feature in shp_lyr:
    #     out_feat.SetGeometry(feature.geometry())
    #     for j in range(feature.GetFieldCount()):
    #         out_feat.SetField(j, feature.GetField(j))
    #     out_lyr.CreateFeature(out_feat)
    #
    # del out_ds
    # del shp_ds
    print("Success........")


def getPolygonEnvelope(vector):

    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(vector,0)
    if ds is None:
        print("Could not open {}".format(vector))
        return -1
    layer = ds.GetLayer()
    numFeatures=layer.GetFeatureCount()
    print("Features number:{}".format(numFeatures))

    # 获取范围
    extent = layer.GetExtent()
    print("Extent:", extent)
    print("UL:", extent[0], extent[3])
    print("LR:", extent[1], extent[2])

    #循环每个要素属性
    for i in range(numFeatures):
        feature = layer.GetNextFeature()
        # 获取字段“id”的属性
        # id = feature.GetField('type')
        # 获取空间属性
        # print(id)
        geometry = feature.GetGeometryRef()
        # x = geometry.GetX()
        polygonextent = geometry.GetEnvelope()
        print(geometry.GetEnvelope())
        # print(y)

        # y = geometry.GetY()
        print("UL:", polygonextent[0], polygonextent[3])
        print("LR:", polygonextent[1], polygonextent[2])




    return 0


if __name__ == '__main__':
    shapefile = '/home/omnisky/PycharmProjects/data/maskRcnn/mytest/onepolygon/262985539_1709e54576_z.shp'
    out = '/home/omnisky/PycharmProjects/data/maskRcnn/mytest/onepolygon/262985539_1709e54576_z.json'
    ChangeToJson(shapefile, out)

    # getPolygonEnvelope(shapefile)
    # fire.Fire()