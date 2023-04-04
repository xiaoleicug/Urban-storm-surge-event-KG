# -*- coding: utf-8 -*-

import math

import pandas as pd
import clr
from ctypes import *

clr.AddReference('GeoSOT')
from GeoSOT import *
import morton
import Spatialcode



x_pi = 3.14159265358979324 * 3000.0 / 180.0

pi = 3.1415926535897932384626 # π

a = 6378245.0 # 长半轴

ee = 0.00669342162296594323 # 偏心率平方

def gcj02_to_bd09(lng, lat):
    """

     火星坐标系(gcJ-02)转百度坐标系(BD-09)

     谷歌、高德——>百度

     :param lng:火星坐标经度

    :param lat:火星坐标纬度

     :return:

    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)

    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)

    bd_lng = z * math.cos(theta) + 0.0065

    bd_lat = z * math.sin(theta) + 0.006

    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """

    百度坐标系(BD-09)转火星坐标系(gcJ-02)

    百度——>谷歌、高德

    :param bd_lat:百度坐标纬度

    :param bd_lon:百度坐标经度

    :return:转换后的坐标列表形式

    """
    x = bd_lon - 0.0065

    y = bd_lat - 0.006

    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)

    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)

    gg_lng = z * math.cos(theta)

    gg_lat = z * math.sin(theta)

    return [gg_lng, gg_lat]





def wgs84_to_gcj02(lng, lat):
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]

    dlat = _transformlat(lng - 105.0, lat - 35.0)

    dlng = _transformlng(lng - 105.0, lat - 35.0)

    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]





def gcj02_to_wgs84(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]

    dlat = _transformlat(lng - 105.0, lat - 35.0)

    dlng = _transformlng(lng - 105.0, lat - 35.0)

    radlat = lat / 180.0 * pi

    magic = math.sin(radlat)

    magic = 1 - ee * magic * magic

    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)

    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)

    mglat = lat + dlat

    mglng = lng + dlng

    return [lng * 2 - mglng, lat * 2 - mglat]





def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)





def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)





def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))

    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret





def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0

    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0

    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0

    return ret





def out_of_china(lng, lat):
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)





if __name__ == '__main__':
    lon = 114.123611
    lat = 22.537961
    #wgs_lon, wgs_lat = gcj02_to_wgs84(lon,lat)
    wgs_lon, wgs_lat = bd09_to_wgs84(lon, lat)
    print(wgs_lon,wgs_lat)
    # print(gcj02_to_wgs84(lon,lat))
    # bd_lon, bd_lat = wgs84_to_bd09(wgs_lon,wgs_lat)
    # print(bd_lon,bd_lat)

    # lon = 114.261455
    # lat = 22.723628
    #
    # wgs_lon, wgs_lat = bd09_to_wgs84(lon,lat)
    #
    # print(wgs_lon,wgs_lat)
    #
    #
    #
    # old_lon, old_lat = wgs84_to_bd09(wgs_lon,wgs_lat)
    #
    # print(old_lon,old_lat)
    #
    # gcj_lon, gcj_lat = bd09_to_gcj02(lon, lat)
    #
    # print(gcj_lon, gcj_lat)
    #
    # gcj_lon, gcj_lat = wgs84_to_gcj02(wgs_lon, wgs_lat)
    #
    # print(gcj_lon, gcj_lat)
    #level = 19
    # with open('.//Weibo//lonlat.txt', 'r', encoding='utf-8') as fin, open('spatial_code.txt', 'w',
    #                                                                 encoding='utf-8') as fout:
    #     fout.write("地点\t经度\t纬度\t空间整数编码\t空间字符串编码\n")
    #     lines = fin.readlines()
    #     for line in lines:
    #         l = line.strip().split()
    #         location_name = l[0]
    #         fout.write(location_name + "\t")
    #         entry_bd09 = l[1].split(",")
    #         wgs_lon, wgs_lat = bd09_to_wgs84(float(entry_bd09[0]), float(entry_bd09[1]))
    #         fout.write(str(wgs_lon) + "\t")
    #         fout.write(str(wgs_lat) + "\t")
    #         level = int(l[2])
    #         _tile = Tile(wgs_lon, wgs_lat, level)
    #         Mgcode = Spatialcode.get_Spatialcode(_tile.gcode, level)
    #         fout.write(str(Mgcode) + "\t")
    #         fout.write(_tile.ToString() + "\n")

    # level =26
    # with open('Subway_entries','r',encoding='utf-8') as fin,open('Subway_entries_wgs','w',encoding='utf-8') as fout:
    #     fout.write("地铁口名称\t经度\t纬度\t空间整数编码\t空间字符串编码\n")
    #     lines = fin.readlines()
    #     for line in lines:
    #         l = line.strip().split()
    #         entry_name = l[0]
    #         entry_bd09 = l[1].split("：")[1].split(",")
    #         wgs_lon, wgs_lat = bd09_to_wgs84(float(entry_bd09[0]),float(entry_bd09[1]))
    #         fout.write(entry_name+"\t")
    #         fout.write(str(wgs_lon)+"\t")
    #         fout.write(str(wgs_lat)+"\t")
    #         _tile = Tile(wgs_lon,wgs_lat,level)
    #         Mgcode = Spatialcode.get_Spatialcode(_tile.gcode,level)
    #         fout.write(str(Mgcode)+"\t")
    #         fout.write(_tile.ToString()+"\n")

            #print(entry_bd09)

# 读取csv格式数据

#     df = pd.read_csv('原始数据路径')
#
# # 新建两列用于储存转换后的坐标
#
#     df['lng_new'] = 0.000000
#
#     df['lat_new'] = 0.000000
#
#     for i in range(0, len(df)):
#
#
#
#         df['lng_new'][i] = bd09_to_wgs84(df['lng'][i], df['lat'][i])[0]
#         #这里的bd09_to_wgs84代表从百度转wgs，你想转啥自己修改就行
#
#         df['lat_new'][i] = bd09_to_wgs84(df['lng'][i], df['lat'][i])[1]
#         #这里的bd09_to_wgs84代表从百度转wgs，你想转啥自己修改就行
#
# # 将转换后的数据另存为新文件
#
#     df.to_csv('输出数据保存路径')
