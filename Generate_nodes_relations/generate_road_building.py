import unittest

from polygon_geosoter.polygon_geosoter import (
    polygon_to_geosots,
    geosot_to_polygon,
    geosots_to_polygon,
    geosots_to_simple,
    spatial_relation_geosots_simple,
    simple_to_geosots
)
from shapely import geometry
from shapely import wkt
from Spatialcode import *
import clr

clr.AddReference('GeoSOT')
from GeoSOT import *


def test_building():
    with open("Building.txt","r",encoding="utf-8") as f:
        lines = f.readlines()
    buildings = []
    fp = open("Test_Building_Polygons.txt","w",encoding="utf-8")
    fp.write("ID:polygon:name\n")
    id = 0
    for line in lines[1:]:
        building = []
        list = line.split("\t")
        p = list[0]
        b_p = wkt.loads(p)
        if len(list)<4:
            name="NULL"
        else:
            name = list[3].strip("\n")

        polygon_After = geosots_to_polygon(polygon_to_geosots(b_p, 22,inner=False))
        simple_polygon_After = geosots_to_simple(polygon_to_geosots(b_p, 22,inner=False))
        #print(simple_polygon_After)
        building.append(simple_polygon_After)
        building.append(name)
        #print(str(id))
        fp.write(str(id)+":"+str(polygon_After)+":"+name)
        fp.write("\n")
        id = id + 1
        buildings.append(building)
    fp.close()
    # G_A = buildings[0]
    # G_B = buildings[1]
    # print(spatial_relation_geosots_simple(G_A,G_B))
    with open("Building_simple.txt","w",encoding="utf-8") as f:
        i = 0
        for id in range(0,len(buildings)):
            f.write(str(id)+"\t")
            f.write(str(buildings[id][0])+"\t")
            f.write(buildings[id][1])
            f.write("\n")
            i = i + 1
    return buildings

def test_road():
    with open("Road_zhugandao.txt","r",encoding="utf-8") as f:
        lines = f.readlines()
    roads = []
    #roads_fclass = []
    #roads_name = []
    fp = open("Test_Road_Polygons.txt","w",encoding="utf-8")
    fp.write("ID:polygon:fclass:name:bridge:tunnel\n")
    id = 0
    for line in lines[1:]:
        road = []
        p = line.split("\t")[0]
        fclass = line.split("\t")[3]
        name = line.split("\t")[4]
        bridge = line.split("\t")[9]
        tunnel = line.split("\t")[10]
        r_p = wkt.loads(p)
        geosots = polygon_to_geosots(r_p, 22,inner=False)
        print(geosots)
        polygon_After = geosots_to_polygon(geosots)
        simple_polygon_After = geosots_to_simple(geosots)
        #print(simple_polygon_After)
        road.append(simple_polygon_After)
        road.append(fclass)
        road.append(name)
        road.append(bridge)
        road.append(tunnel)
        #print(str(id))
        fp.write(str(id)+":"+str(polygon_After)+":"+fclass+":"+name)
        fp.write("\n")
        id = id + 1
        roads.append(road)
    fp.close()
    # G_A = buildings[0]
    # G_B = buildings[1]
    # print(spatial_relation_geosots_simple(G_A,G_B))
    with open("Road_simple.txt","w",encoding="utf-8") as f:
        i = 0
        for id in range(0,len(roads)):
            f.write(str(id)+"\t")
            f.write(str(roads[id][0])+"\t")
            f.write(roads[id][1]+"\t")
            f.write(roads[id][2]+"\t")
            f.write(roads[id][3] + "\t")
            f.write(roads[id][4])
            f.write("\n")
            i = i + 1
    return roads

def test_Shenzhen():
    with open("E:\\GeohazardsKG\\Typhoon_Shenzhen_KG\\Shenzhen_prov\\深圳_省界_polygon.txt","r") as f:
        lines = f.readlines()
    geosots = set()
    for line in lines[1:]:
        p = line.split("\t")[0]
        polygon = wkt.loads(p)
        geosots=geosots|polygon_to_geosots(polygon,13,False)
    fp = open("Test_Shenzhen_Polygons.txt", "w")
    fp.write("ID:polygon:geo_string:geocode\n")
    id = 0
    for geo in geosots:
        polygon = geosot_to_polygon(geo)
        if polygon.area<=32*32*1000000:
            Mgcode = get_Spatialcode(Tile(geo).gcode,13)
            fp.write(str(id) + ":" + str(polygon)+":"+geo+":"+str(Mgcode))
            fp.write("\n")
            id = id+1
        else:
            print(id)
    fp.close()

def output_search_polygon():
    spatial_range = ('G001130221-12', {0: (1, 1), 1: (0, 1), 2: (1, 1)})
    spatial_range_group = simple_to_geosots(spatial_range)  # 查询范围的空间编码集合
    polygon = geosots_to_polygon(spatial_range_group)
    fout = open("search_polygon.txt", "w", encoding="utf-8")
    fout.write("ID:polygon:geo_string\n")
    i = 0
    fout.write("0:"+str(polygon)+ ":" + str(spatial_range))
    for f in spatial_range_group:
        polygon = geosot_to_polygon(f)
        i = i + 1
        fout.write(str(i) + ":" + str(polygon) + ":" + f )
        fout.write("\n")
    fout.close()


if __name__ == "__main__":
    #test_Shenzhen()
    #test_Shenzhen_distincts()
    test_building()
    test_road()

