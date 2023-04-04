import clr
from ctypes import *
clr.AddReference('GeoSOT')
from GeoSOT import *
import queue

from shapely import geometry
from shapely.ops import cascaded_union



def geosot_to_polygon(geo):
    """
    :param geo: String that represents the geosot.
    :return: Returns a Shapely's Polygon instance that represents the geohash.
    """
    bbox = Tile(geo).GetBbox()
    corner_1 =(bbox.West, bbox.South)
    corner_2 =(bbox.East, bbox.South)
    corner_3 =(bbox.East, bbox.North)
    corner_4 =(bbox.West, bbox.North)
    # lat_centroid, lng_centroid, lat_offset, lng_offset = geohash.decode_exactly(geo)
    #
    # corner_1 = (lat_centroid - lat_offset, lng_centroid - lng_offset)[::-1]
    # corner_2 = (lat_centroid - lat_offset, lng_centroid + lng_offset)[::-1]
    # corner_3 = (lat_centroid + lat_offset, lng_centroid + lng_offset)[::-1]
    # corner_4 = (lat_centroid + lat_offset, lng_centroid - lng_offset)[::-1]

    return geometry.Polygon([corner_1, corner_2, corner_3, corner_4, corner_1])

def polygon_to_geosots(polygon, level, inner=True):
    """
    :param polygon: shapely polygon.
    :param level: int. Geosots' level that form resulting polygon.
    :param inner: bool, default 'True'. If false, geosots that are completely outside from the polygon are ignored.
    :return: set. Set of geosots that form the polygon.
    """
    inner_geosots = set()
    outer_geosots = set()

    envelope = polygon.envelope
    centroid = polygon.centroid
    center_dms = LngLat(centroid.y,centroid.x).ToString()
    testing_geosots = queue.Queue()
    testing_geosots.put(Tile(center_dms,level).ToString())

    while not testing_geosots.empty():
        current_geosot = testing_geosots.get()

        if (
            current_geosot not in inner_geosots
            and current_geosot not in outer_geosots
        ):
            current_polygon = geosot_to_polygon(current_geosot)

            condition = (
                envelope.contains(current_polygon)
                if inner
                else envelope.intersects(current_polygon)
            )

            if condition:
                if inner:
                    if polygon.contains(current_polygon):
                        inner_geosots.add(current_geosot)
                    else:
                        outer_geosots.add(current_geosot)
                else:
                    if polygon.intersects(current_polygon):
                        inner_geosots.add(current_geosot)
                    else:
                        outer_geosots.add(current_geosot)
                for neighbor in Tile(current_geosot).Getneighbors(current_geosot):
                    if (
                        neighbor not in inner_geosots
                        and neighbor not in outer_geosots
                    ):
                        testing_geosots.put(neighbor)

    return inner_geosots

def geosots_to_simple(geosots):
    """
    :param geosots: array-like. List of geosots to a polygon.
    :return: simple representation for the polygon, i.e., (C0,{i:ji-ki}).
    """
    XY_array = {}
    X_set =set()
    #l = Tile(geosots[0]).Level
    for g in geosots:
        if not Tile(g).Y in XY_array:
            XY_array[Tile(g).Y]=[]
            l = Tile(g).Level
        XY_array[Tile(g).Y].append(Tile(g).X)
        X_set.add(Tile(g).X)

    X_min = min(X_set)
    X_max = max(X_set)
    Y_min = min(XY_array.keys(),key=(lambda x:x))
    Y_max = max(XY_array.keys(), key=(lambda x: x))

    print(X_set)
    print(XY_array.keys())

    MN_array ={}
    for i in range(0,Y_max-Y_min+1):
        if Y_min+i not in XY_array:
            continue
        # if i not in MN_array:

        jk_list = sorted(XY_array[Y_min+i])
        j = jk_list[0]-X_min
        k = jk_list[-1]-X_min
        MN_array[i]=(j,k)

    C0 = Tile(l, X_min, Y_min).ToString()
    return (C0,MN_array)

def simple_to_geosots(geosot_group):
    C0 = geosot_group[0]
    MN_array = geosot_group[1]
    X_min = Tile(C0).X
    Y_min = Tile(C0).Y
    l = Tile(C0).Level
    geosots=[]
    for y in MN_array:
        j=MN_array[y][0]+X_min
        k=MN_array[y][1]+X_min
        for x in range(j,k+1):
            geosots.append(Tile(l,x,y+Y_min).ToString())
    return geosots


def spatial_relation_geosots_simple(G_A,G_B):
    CO_A = G_A[0]
    C0_B = G_B[0]
    level = max(Tile(CO_A).Level, Tile(C0_B).Level)
    A_xmin = Tile(CO_A).X
    B_xmin = Tile(C0_B).X
    A_ymin = Tile(CO_A).Y
    B_ymin = Tile(C0_B).Y
    X_min = min(A_xmin,B_xmin)
    Y_min = min(A_ymin,B_ymin)

    C0_new = Tile(level,X_min,Y_min).ToString()
    MN_array_A = {}
    n_a = 0
    #for i in range(0,len(G_A[1])):
    for i in list(G_A[1].keys()):
        MN_array_A[i+(A_ymin-Y_min)] = (G_A[1][i][0]+(A_xmin-X_min),G_A[1][i][1]+(A_xmin-X_min))
        n_a = n_a+(G_A[1][i][1]-G_A[1][i][0])+1
    G_A_new = (C0_new,MN_array_A)
    MN_array_B = {}
    n_b = 0
    #for i in range(0, len(G_B[1])):
    for i in list(G_B[1].keys()):
        MN_array_B[i+(B_ymin-Y_min)] = (G_B[1][i][0] + (B_xmin - X_min), G_B[1][i][1] + (B_xmin - X_min))
        n_b = n_b + (G_B[1][i][1] - G_B[1][i][0]) + 1
    G_B_new = (C0_new, MN_array_B)
    flag_touch = False
    n_equal = 0
    same_Y = set(MN_array_A).intersection(MN_array_B)
    min_A = A_ymin-Y_min
    min_B = B_ymin-Y_min
    max_A = max(MN_array_A.keys())
    max_B = max(MN_array_B.keys())
    if len(same_Y) == 0:
        r = "disjoint"
        if min_A == (max_B + 1):
            if MN_array_A[min_A][1] >= MN_array_B[min_A - 1][0] - 1 & MN_array_A[min_A][1] <= MN_array_B[min_A - 1][
                1] + 1:
                r = "touch"
            if MN_array_A[min_A][0] >= MN_array_B[min_A - 1][0] - 1 & MN_array_A[min_A][0] <= MN_array_B[min_A - 1][
                1] + 1:
                r = "touch"
        if min_B == (max_A + 1):
            if MN_array_B[min_B][1] >= MN_array_A[min_B - 1][0] - 1 & MN_array_B[min_B][1] <= MN_array_A[min_B - 1][
                1] + 1:
                r = "touch"
            if MN_array_B[min_B][0] >= MN_array_A[min_B - 1][0] - 1 & MN_array_B[min_B][0] <= MN_array_A[min_B - 1][
                1] + 1:
                r = "touch"
        return (G_A, r, G_B)
    for i in same_Y:
        ja,ka = MN_array_A[i]
        jb,kb = MN_array_B[i]
        if ka==jb-1 | kb==ja-1:
            flag_touch = True
        if ka > jb & jb > ja:
            n_equal = n_equal+ka-jb
        if kb>ja & ja>jb:
            n_equal = n_equal+kb-ja
    #print(n_equal)
    if n_equal ==0:
        if flag_touch:
            r ="touch"
        else:
            r = "disjoint"
        return (G_A,r,G_B)
    else:
        if n_equal==n_b & n_b<n_a:
            r = "contains"
            return (G_A,r,G_B)
        else:
            if n_equal == n_a & n_a < n_b:
                r = "contained_by"
                return (G_A, r, G_B)
            else:
                if flag_touch:
                    r = "touch"
                    return (G_A,r,G_B)
                else:
                    r = "overlap"
                    return (G_A,r,G_B)




def geosots_to_polygon(geosots):
    """
    :param geosots: array-like. List of geosots to form resulting polygon.
    :return: shapely geometry. Resulting Polygon after combining geosots.
    """
    return cascaded_union([geosot_to_polygon(g) for g in geosots])
