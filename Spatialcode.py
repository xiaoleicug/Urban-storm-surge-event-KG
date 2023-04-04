import clr
from ctypes import *

clr.AddReference('GeoSOT')
from GeoSOT import *
import morton

def get_Spatialcode(geosot_id, level):
    m = 64
    O_MScale_gcode = (1 << (m - 2 - level - level)) - 1
    MScale_gcode = O_MScale_gcode + (geosot_id << (m - 1 - level - level))
    return MScale_gcode


def get_level(MScale_gcode):
    m = 32
    n = 6
    level = 0
    if MScale_gcode & 1 == 0:
        level = m - 1
    else:
        Mid = (MScale_gcode - 1) ^ (MScale_gcode + 1)
        #print(bin(Mid))
        for i in range(n, 0, -1):
            Mask1 = 0
            b = (1 << i) - 1
            e = (1 << (i - 1)) - 1
            for k in range(b, e, -1):
                Mask1 = (1 << k) + Mask1
            Mid0 = (Mid & Mask1) >> (1 << (i - 1))
            if Mid0 == 0:
                Mask2 = 0
                e = 1 << (i - 1)
                for k in range(0, e):
                    Mask2 = (1 << k) + Mask2
                Mid = Mid & Mask2
                level = level + (1 << (i - 1))
            else:
                Mid = Mid0
        level = level >> 1
    return level

def convert2dms(MScale_gcode):
    m = 64
    level = get_level(MScale_gcode)
    O_MScale_gcode = (1 << (m - 2 - level - level)) - 1
    geosot_id = (MScale_gcode - O_MScale_gcode) >> (m - 1 - level - level)
    Morton2D = morton.Morton(dimensions=2, bits=31)
    (X, Y) = Morton2D.unpack(geosot_id)
    dms = Tile(level, X, Y)
    #print(dms)
    return dms



def get_neighbor_gridcodes(MScale_gcode):
    m = 64
    level = get_level(MScale_gcode)
    O_MScale_gcode = (1 << (m - 2 - level - level)) - 1
    geosot_id = (MScale_gcode - O_MScale_gcode) >> (m - 1 - level - level)
    X = 0
    Y = 0
    Morton2D = morton.Morton(dimensions=2, bits =31)
    (X,Y) = Morton2D.unpack(geosot_id)
    # Morton2D.Magicbits(geosot_id, X, Y)
    It_N = 1
    Eight_neighbors = []
    Eight_neighbors.append(Morton2D.pack(X - It_N, Y + It_N))
    Eight_neighbors.append(Morton2D.pack(X, Y + It_N))
    Eight_neighbors.append(Morton2D.pack(X + It_N, Y + It_N))
    Eight_neighbors.append(Morton2D.pack(X + It_N, Y))
    Eight_neighbors.append(Morton2D.pack(X + It_N, Y - It_N))
    Eight_neighbors.append(Morton2D.pack(X, Y - It_N))
    Eight_neighbors.append(Morton2D.pack(X - It_N, Y - It_N))
    Eight_neighbors.append(Morton2D.pack(X - It_N, Y))

    for i in range(0, 8):
        Eight_neighbors[i] = get_Spatialcode(Eight_neighbors[i], level)

    return Eight_neighbors


def get_son_gridcodes(MScale_gcode, level_son):
    m = 64
    level = get_level(MScale_gcode)
    Mc0 = (1 << (62 - level - level)) - (1 << (62 - level_son - level_son))
    A = MScale_gcode - Mc0
    B = MScale_gcode + Mc0
    interval = 1<<(31-level_son)
    return range(A,B+1,interval)



def get_father_gridcode(MScale_gcode, level_father):
    m = 64
    level = get_level(MScale_gcode)
    FMc0 =(1<<(62-level_father-level_father))-1
    delta_FMc = (MScale_gcode>> (m-1-level_father-level_father))<<(m-1-level_father-level_father)
    FMc = FMc0 + delta_FMc

    return FMc

def get_spatial_relation(MTc1, MTc2):
    if MTc2 == MTc1:
        r = "equal"
        return (MTc1,r,MTc2)
    level_A = get_level(MTc1)
    level_B = get_level(MTc2)
    if level_A == level_B:
        if MTc2 in get_neighbor_gridcodes(MTc1):
            r = "touch"
            return (MTc1,r,MTc2)
        else:
            r = "disjoint"
            return (MTc1,r,MTc2)
    elif level_A > level_B:
        new_MTc2 = get_son_gridcodes(MTc2,level_A)
        if MTc1 in new_MTc2:
            r = "contained_by"
            return (MTc1,r,MTc2)
        else:
            for m in new_MTc2:
                if MTc1 in get_neighbor_gridcodes(m):
                    r="touch"
                    return (MTc1,r,MTc2)
            r = "disjoint"
            return (MTc1,r,MTc2)
    else:
        new_MTc1 = get_son_gridcodes(MTc1,level_B)
        if MTc2 in new_MTc1:
            r = "contain"
            return (MTc1,r,MTc2)
        else:
            for m in new_MTc1:
                if MTc2 in get_neighbor_gridcodes(m):
                    r = "touch"
                    return (MTc1,r,MTc2)
            r = "disjoint"
            return (MTc1,r,MTc2)





if __name__ == "__main__":
    dms = "22° 35' 43.0144\" N, 114° 18' 9.2949\" E"
    level = 17
    _tile = Tile(dms, level)
    print(_tile.ToString())
    Mgcode = get_Spatialcode(_tile.gcode,level)
    print(Mgcode)



    # print(get_level(Mgcode))
    # print(get_level(321854111743))
    # print(convert2dms(321854111743).Corner)
    # neighbors = get_neighbor_gridcodes(Mgcode)
    # print(neighbors)
    # print(len(get_son_gridcodes(Mgcode, level+2)))
    # print(get_father_gridcode(Mgcode, level-2))
    # Mgcode2 = get_father_gridcode(Mgcode, level-2)
    # print(get_level(Mgcode2))
    # print(convert2dms(Mgcode2).Corner)
    # for neighbor in neighbors:
    #     print(convert2dms(neighbor).Corner)
    # print(get_spatial_relation(Mgcode,Mgcode2))
    # Mgcode3 = 263274034886606847
    # print(get_spatial_relation(Mgcode, Mgcode3))

    # f1=open("flood_grid.txt","r",encoding="utf-8")
    # f2=open("./Test/Test_Shenzhen_Polygons.txt","r",encoding="utf-8")
    # flood_mgcodes = []
    # pop_mgcodes=[]
    # for line in f1:
    #     flood_mgcodes.append(line.split()[0])
    # for line in f2:
    #     pop_mgcodes.append(line.split(":")[-1].strip())
    # for m in flood_mgcodes:
    #     m_sons = get_son_gridcodes(int(m),19)
    #     print("The sons of grid " + m + "are: ")
    #     #print(list(set(m_sons)&set(pop_mgcodes[1:])))
    #     for m_s in m_sons:
    #         if str(m_s) in pop_mgcodes[1:]:
    #             print(str(m_s)+"\t")
    #     print("\n")
    # f1.close()
    # f2.close()



