import Spatialcode
from polygon_geosoter.polygon_geosoter import (
    polygon_to_geosots,
    geosot_to_polygon,
    geosots_to_polygon,
    geosots_to_simple,
    spatial_relation_geosots_simple
)
import Timecode
from datetime import datetime
# from scipy.io import netcdf_file
#import netCDF4
import nc
from netCDF4 import Dataset
import numpy as np
import clr
clr.AddReference('GeoSOT')
from GeoSOT import *
import haversine
import compute_same_nodes
import morton
import os
import logging
import json
#from scipy.spatial import cKDTree
import math
import copy



def load_netcdf(inp_path):
    """
    Open the nc file and read the required data.
    :return: the value for the required parameters
    """
    value = {}
    required_var = ['lon', 'lat', 'lonc', 'latc', 'h', 'zeta','Times']
    nc_obj = Dataset('E:\\GeohazardsKG\\Typhoon_Shenzhen_KG\\szsea_0001.nc')
    # print(nc_obj.variables.keys())
    # print(np.array(nc_obj.variables['zeta'][:]))
    for key in required_var:
        value[key]=np.array(nc_obj.variables[key][:])
    value['flow'] = value['zeta']
    # value['depth'] = np.max(value['zeta'] + value['h'], axis=0)
    value['depth'] = value['zeta'] + value['h']
    value.pop('h')
    value.pop('zeta')
    value['times']=[]
    for i in range(0,432):
        t = []
        for b in value['Times'][i]:
            t.append(b.decode())
        value['times'].append(''.join(t))

    # with netcdf_file(inp_path, 'r', False) as nf:
    #     for key in required_var:
    #         value[key] = np.array(nf.variables[key][:])
    # value['flow'] = value['zeta']
    # # value['depth'] = np.max(value['zeta'] + value['h'], axis=0)
    # value['depth'] = value['zeta'] + value['h']
    # value.pop('h')
    # value.pop('zeta')
    return value

def on_land_checker(data):
    """
    Filter the on land points by the Border object
    :return:
    """
    # cut the region to the shenzhen area
    # coordinate_range = [113, 53, 114, 0, 22, 23]
    lon_range = np.where((data['lon'] > 113.7) & (data['lon'] < 114.63))
    #lat_range = np.where(data['lat'] > 22.4)
    # lon_range = np.where((self.data['lon'] > 113.7) & (self.data['lon'] < 114.0))
    lat_range = np.where((data['lat'] > 22.4) & (data['lat'] < 23))
    inside_range = np.intersect1d(lat_range[0], lon_range[0])
    # coords = zip(self.data['lon'][inside_range], self.data['lat'][inside_range])
    # return inside_range[np.where([self.boundary.inside_checker(c) for c in coords])]
    return inside_range

def extract_flood_loc(value):
    """
    Extract flood location
    :return: nothing
    """
    # find the inundation area by the depth
    flood_data = []
    flood_index_4 = [np.where((np.array(dep) > 0.05) & (np.array(dep)< 0.2)) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data4 = [
        [
            np.array(value['lon'])[index],
            np.array(value['lat'])[index],
            np.array(value['depth'][n])[index]
        ]
        for n, index in enumerate(flood_index_4)
    ]
    flood_data.append(data4)
    flood_index_3 = [np.where((np.array(dep) >= 0.2) & (np.array(dep)< 0.5)) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data3 = [
        [
            np.array(value['lon'])[index],
            np.array(value['lat'])[index],
            np.array(value['depth'][n])[index]
        ]
        for n, index in enumerate(flood_index_3)
    ]
    flood_data.append(data3)
    flood_index_2 = [np.where((np.array(dep) >= 0.5) & (np.array(dep) <= 0.8)) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data2 = [
        [
            np.array(value['lon'])[index],
            np.array(value['lat'])[index],
            np.array(value['depth'][n])[index]
        ]
        for n, index in enumerate(flood_index_2)
    ]
    flood_data.append(data2)
    flood_index_1 = [np.where(np.array(dep)>0.8) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data1 = [
        [
            np.array(value['lon'])[index],
            np.array(value['lat'])[index],
            np.array(value['depth'][n])[index]
        ]
        for n, index in enumerate(flood_index_1)
    ]
    flood_data.append(data1)
    return flood_data

def extract_flood_loc_code(value, spatial_level,time_level):
    """
    Extract flood location
    :return: nothing
    """
    # find the inundation area by the depth
    Mgcodes = np.array(Latlng_Spatialcode(value['lon'],value['lat'],spatial_level))
    Timecodes = times_Timecode(value, time_level)
    flood_data = []
    flood_index_4 = [np.where((np.array(dep) > 0.05) & (np.array(dep)< 0.2)) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data4 = []
    for n, index in enumerate(flood_index_4):
        lon = np.array(value['lon'])[index]
        lat = np.array(value['lat'])[index]
        # Mgcode = Spatialcode.get_Spatialcode(Tile(lon,lat, spatial_level).gcode, spatial_level)
        # Mgcode_list = Latlng_Spatialcode(lon, lat, spatial_level)
        Mgcode_list = []
        for i in index:
            Mgcode_list.append(Mgcodes[i])
        depth = np.array(value['depth'][n])[index]
        MTcode = Timecodes[n]
        data4.append([Mgcode_list, MTcode, depth])

    # data4 = [
    #     [
    #         np.array(value['lon'])[index],
    #         np.array(value['lat'])[index],
    #         np.array(value['depth'][n])[index]
    #     ]
    #     for n, index in enumerate(flood_index_4)
    # ]
    flood_data.append(data4)
    flood_index_3 = [np.where((np.array(dep) >= 0.2) & (np.array(dep)< 0.5)) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data3 = []
    for n, index in enumerate(flood_index_3):
        lon = np.array(value['lon'])[index]
        lat = np.array(value['lat'])[index]
        # Mgcode = Spatialcode.get_Spatialcode(Tile(lon,lat, spatial_level).gcode, spatial_level)
        # Mgcode_list = Latlng_Spatialcode(lon, lat, spatial_level)
        Mgcode_list = []
        for i in index:
            Mgcode_list.append(Mgcodes[i])
        depth = np.array(value['depth'][n])[index]
        MTcode = Timecodes[n]
        data3.append([Mgcode_list, MTcode, depth])
    # data3 = [
    #     [
    #         np.array(value['lon'])[index],
    #         np.array(value['lat'])[index],
    #         np.array(value['depth'][n])[index]
    #     ]
    #     for n, index in enumerate(flood_index_3)
    # ]
    flood_data.append(data3)
    flood_index_2 = [np.where((np.array(dep) >= 0.5) & (np.array(dep) <= 0.8)) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data2 = []
    for n, index in enumerate(flood_index_2):
        lon = np.array(value['lon'])[index]
        lat = np.array(value['lat'])[index]
        # Mgcode = Spatialcode.get_Spatialcode(Tile(lon,lat, spatial_level).gcode, spatial_level)
        # Mgcode_list = Latlng_Spatialcode(lon, lat, spatial_level)
        Mgcode_list = []
        for i in index:
            Mgcode_list.append(Mgcodes[i])
        depth = np.array(value['depth'][n])[index]
        MTcode = Timecodes[n]
        data2.append([Mgcode_list, MTcode, depth])
    # data2 = [
    #     [
    #         np.array(value['lon'])[index],
    #         np.array(value['lat'])[index],
    #         np.array(value['depth'][n])[index]
    #     ]
    #     for n, index in enumerate(flood_index_2)
    # ]
    flood_data.append(data2)
    flood_index_1 = [np.where(np.array(dep)>0.8) for dep in value['depth']]
    # create list, [[lon, lat, depth] -> each time interval, ...]
    data1 = []
    for n, index in enumerate(flood_index_1):
        lon = np.array(value['lon'])[index]
        lat = np.array(value['lat'])[index]
        #Mgcode = Spatialcode.get_Spatialcode(Tile(lon,lat, spatial_level).gcode, spatial_level)
        # Mgcode_list = Latlng_Spatialcode(lon, lat, spatial_level)
        Mgcode_list = []
        for i in index:
            Mgcode_list.append(Mgcodes[i])
        depth = np.array(value['depth'][n])[index]
        MTcode = Timecodes[n]
        data1.append([Mgcode_list,MTcode,depth])
    # data1 = [
    #     [
    #         np.array(value['lon'])[index],
    #         np.array(value['lat'])[index],
    #         np.array(value['depth'][n])[index]
    #     ]
    #     for n, index in enumerate(flood_index_1)
    # ]
    flood_data.append(data1)
    return flood_data

def Latlng_Spatialcode(lon_list,lat_list, level):
    Mgcodes = []
    for i in range(len(lon_list)):
        lon = lon_list[i].item()
        lat = lat_list[i].item()
        dms_string = LngLat(lat,lon).ToString()
        _tile = Tile(dms_string,level)
        # print(_tile.ToString())
        Mgcode = Spatialcode.get_Spatialcode(_tile.gcode,level)
        Mgcodes.append(Mgcode)
    return Mgcodes

def times_Timecode(value_times,level):
    Timecodes = []
    for time in value_times:
        datetime_tc = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
        MTc = Timecode.get_Timecode(datetime_tc, level)
        # print(Timecode.convertcode2str(MTc))
        Timecodes.append(MTc)
    return Timecodes

# 网格中心坐标 centeroid.x, centeroid.y; 同一网格编码的node点
# 反距离加权 得到每个网格对应的depth
def get_center_depth(lon,lat,lst):
    p0=(lat,lon)
    sum0=0
    sum1=0
    temp=[]
    for point in lst:
        if lat == point[0] and lon == point[1]:
            return point[2]
        p1 = (point[0],point[1])
        Di = haversine.haversine(p1, p0, unit=haversine.Unit.METERS)
        ptn = copy.deepcopy(list(point))
        ptn.append(Di)
        temp.append(ptn)
    for point in temp:
        sum0+=point[2]/point[3]
        sum1+=1/point[3]
    return sum0/sum1

if __name__ == "__main__":
    value = load_netcdf('E:\\GeohazardsKG\\Typhoon_Shenzhen_KG\\szsea_0001.nc')
    value_SZ = on_land_checker(value)
    #net = nc.NetCDFFile(input_path='E:\\GeohazardsKG\\Typhoon_Shenzhen_KG\\szsea_0001.nc',output_path='E:\\GeohazardsKG\\Typhoon_Shenzhen_KG\\szsea_0002.nc',pre_trigger=True)
    #value = net.load_netcdf()
    #flood_data= extract_flood_loc(value)
    # print(flood_data)
    spatial_level = 17
    Mgcodes = Latlng_Spatialcode(value['lon'][value_SZ],value['lat'][value_SZ],spatial_level)
    print(len(Mgcodes))
    time_level = 19
    print(value['times'])
    Timecodes = times_Timecode(value['times'],time_level)
    print(Timecodes)
    print(len(Timecodes))
    # 计算不重复的node
    same_nodes_code = compute_same_nodes.get_lst(Mgcodes)[0]
    same_nodes_index_list = compute_same_nodes.get_lst(Mgcodes)[1]
    depth_list = []
    water_out= open('multitime_depth.txt','w')
    water_out.write(str(list(same_nodes_code)))
    water_out.write("\n")
    with open('E:\\GeohazardsKG\\Typhoon_Shenzhen_KG\\Shenzhen_waternode.txt','r') as Shenzhenwater_in:
        lines = Shenzhenwater_in.readlines()
    same_node_range_of_Shenzhen = []
    for line in lines[1:]:
        number = line.split("\t")[1]
        same_node_range_of_Shenzhen.append(int(number))
    fp1 = open('flood_grid.txt', 'w')  # 输出 Mgcode,(Geostring),timecode,depth,flood_level
    #for t in range(0, 1):
    for t in range(0,len(value['times'])):
        value_combine = list(zip(value['lat'][value_SZ],value['lon'][value_SZ],value['depth'][t][value_SZ]))
        depth_list_at_t = []
        #fp = open('Waternode_all.txt', 'w')

        #fp.write("name:polygon:geocode:geostring\n")

        #for i in range(0,len(same_nodes_code)):
        for i in same_node_range_of_Shenzhen:
            #print(Spatialcode.convert2dms(int(same_nodes_code[i])))
            Geostring = Spatialcode.convert2dms(int(same_nodes_code[i])).ToString()
            grid = geosot_to_polygon(Geostring)
            # fp.write(str(i)+":"+ str(grid)+":"+str(same_nodes_code[i])+":"+Geostring)
            # fp.write("\n")
            centroid = grid.centroid
            same_nodes_list = [value_combine[j] for j in same_nodes_index_list[i]]
            grid_depth = get_center_depth(centroid.x,centroid.y,same_nodes_list)
            if grid_depth>=0.05 and grid_depth<0.5:
                #print(t)
                fp1.write(str(same_nodes_code[i])+"\t"+Geostring+"\t"+str(Timecodes[t])+"\t"+str(grid_depth)+"\t"+"V")
                fp1.write("\n")
            if grid_depth>=0.5 and grid_depth<0.8:
                #print(t)
                fp1.write(str(same_nodes_code[i])+"\t"+Geostring+"\t"+str(Timecodes[t])+"\t"+str(grid_depth)+"\t"+"IV")
                fp1.write("\n")
            if grid_depth>=0.8 and grid_depth<1.2:
                #print(t)
                fp1.write(str(same_nodes_code[i])+"\t"+Geostring+"\t"+str(Timecodes[t])+"\t"+str(grid_depth)+"\t"+"III")
                fp1.write("\n")
            if grid_depth>=1.2 and grid_depth<3:
                        #print(t)
                fp1.write(str(same_nodes_code[i])+"\t"+Geostring+"\t"+str(Timecodes[t])+"\t"+str(grid_depth)+"\t"+"II")
                fp1.write("\n")
            if grid_depth>=3:
                #print(t)
                fp1.write(str(same_nodes_code[i])+"\t"+Geostring+"\t"+str(Timecodes[t])+"\t"+str(grid_depth)+"\t"+"I")
                fp1.write("\n")

            #print(grid_depth)
            depth_list_at_t.append(grid_depth)
        depth_list.append(depth_list_at_t)
        print(t)
        water_out.write(str(depth_list_at_t))
        water_out.write("\n")
    print("End!")
    water_out.close()
    #code_depth_list = list(zip(same_nodes_code,depth_list))
    #print(code_depth_list)
    #fp.close()
    fp1.close()
    # print(value['times'])
    # time_level = 19
    # flood_data = extract_flood_loc_code(value,spatial_level,time_level)
    # print(flood_data)
    #Timecodes = times_Timecode(value,time_level)
    # print(Timecodes)



