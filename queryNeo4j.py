# -*- coding: utf-8 -*-
from py2neo import Node, Graph, Relationship, Subgraph
import networkx as nx

import pandas as pd
import re
import numpy as np
from pandas import DataFrame

import Spatialcode
from polygon_geosoter.polygon_geosoter import (
    polygon_to_geosots,
    geosot_to_polygon,
    geosots_to_polygon,
    geosots_to_simple,
    simple_to_geosots,
    spatial_relation_geosots_simple
)
import time
import Timecode
class QueryforNeo4j(object):
    graph = Graph("http://127.0.0.1//:7474", username="neo4j", password="xiaolei@226")

    def query_spatial_range(self):
        Spatial_range=self.graph.run("match (n:Spatial_grid_group{GeoSOT_grids:\"('G001130221-12', {0: (1,1), 1: (0, 1), 2: (1, 1)})\"}) return n").data()
        print(Spatial_range)
        spatial_range = ('G001130221-12', {0: (1,1), 1: (0, 1), 2: (1, 1)})
        #spatial_range = ('G001130230-21030', {0: (0, 1), 1: (1, 1)})
        #spatial_range=('G001130230-21', {0: (0, 0)})
        print(spatial_range)

        spatial_range_group = simple_to_geosots(spatial_range)  #查询范围的空间编码集合
        print(spatial_range_group)
        spatial_nodes_inrange=[]    # 在查询范围内或者与查询范围相交的空间节点集合

        spatial_nodes = self.graph.run("match (n:Spatial_grid_group)<-[:inPlace]-()<-[:has_influenced]-() return distinct n").data()  #返回所有受灾了的空间节点

        print(len(spatial_nodes))
        count_disaster_nodes = 0
        count_influnced_hbb = 0
        count_influnced_road = 0
        count_influnced_building = 0
        st=time.time()
        for spatial_node in spatial_nodes:
            geosot_grids = simple_to_geosots(eval(spatial_node['n']["GeoSOT_grids"]))  #空间节点对应的空间编码集合
            flag = True
            count = 0
            for geosot in geosot_grids:
                for r in spatial_range_group:
                    if flag:
                        if geosot.startswith(r):
                            #count = count+1
                            #if count == len(geosot_grids):
                            spatial_nodes_inrange.append(spatial_node)
                            gs=spatial_node['n']["GeoSOT_grids"]
                            influenced_road_nodes_inrange = self.graph.run(
                                "match (n:Spatial_grid_group{GeoSOT_grids:\"" + gs + "\"})<-[:inPlace]-(r:Road)<-[i:has_influenced]-(f) where f.flooded_depth>0.15 return distinct(r)").data()
                            # num_disaster_nodes_inrange = self.graph.run(
                            #     "match (n:Spatial_grid_group{GeoSOT_grids:\"" + gs + "\"})<-[:inPlace]-()<-[:has_influenced]-(f) where f.flooded_depth>0.15 return count(f)").data()[
                            #     0]['count(f)']
                            # count_disaster_nodes = count_disaster_nodes + num_disaster_nodes_inrange
                            influenced_building_nodes_inrange = self.graph.run(
                                "match (n:Spatial_grid_group{GeoSOT_grids:\"" + gs + "\"})<-[:inPlace]-(r:Building)<-[i:has_influenced]-(f)  return distinct(r)").data()
                            count_influnced_hbb = count_influnced_hbb + len(influenced_road_nodes_inrange)+len(influenced_building_nodes_inrange)
                            count_influnced_road = count_influnced_road+ len(influenced_road_nodes_inrange)
                            count_influnced_building = count_influnced_building + len(influenced_building_nodes_inrange)

                            flag = False
                            break
                    else:
                        break
        #print(count_disaster_nodes)
        ed = time.time()
        print(str(ed-st)+" s")
        print(spatial_range_group)
        print(count_influnced_hbb)
        print(count_influnced_building)
        print(count_influnced_road)

        print(len(spatial_nodes_inrange))



        #
        #     rel = spatial_relation_geosots_simple(spatial_range, geosot_grids)[1]
        #     if rel == 'contains':
        #         spatial_nodes_inrange.append(spatial_node['n'])

        #print(spatial_nodes_inrange)

    def query_temporal_range(self):
        #Temporal_range = Timecode.get_Timecode_containment(3837919231)  # 20180916
        Temporal_range_st = Timecode.get_Timecode_containment(3837947903)
        Temporal_range_ed = Timecode.get_Timecode_containment(3837954623)

        A = Temporal_range_st[0]
        B = Temporal_range_ed[1]
        st = time.time()
        time_nodes = self.graph.run("match (t:Time) return t").data()
        print(len(time_nodes))

        time_codes_inrange=[]
        for t in time_nodes:
            t_c = t['t']["Time_code"]
            a = Timecode.get_Timecode_containment(t_c)[0]
            b = Timecode.get_Timecode_containment(t_c)[1]
            if a>=A and b<= B:
                time_codes_inrange.append(t_c)
        #affected_Road_intimerange=[]
        count_road = 0
        count_building = 0
        print(len(time_codes_inrange))
        for t_c in time_codes_inrange:
            affected_Road_intimerange=self.graph.run("match (r:Road)<-[:has_influenced]-(f:Road_flooded)-[:at_Time]->(:Time{Time_code:"+str(t_c)+"}) where f.flooded_depth>0.15 return distinct r").data()
            count_road = count_road+ len(affected_Road_intimerange)

        for t_c in time_codes_inrange:
            affected_Building_intimerange=self.graph.run("match (b:Building)<-[:has_influenced]-(f:Building_flooded)-[:at_Time]->(:Time{Time_code:"+str(t_c)+"}) return distinct b").data()
            count_building = count_building+ len(affected_Building_intimerange)

        ed = time.time()
        print(str(ed-st)+" s")
        print(count_road)
        print(count_building)



    def create_nodeandrelation(self):
        flood_grid_nodes=self.graph.run("MATCH (n:flood_grid) where n.Level=\"I\" RETURN n").data()
        #nodes = []
        #rels = []
        i=0
        for f_n in flood_grid_nodes:
            f_mgcode = f_n['n']['GeoSOT_string']
            f_timecode = f_n['n']['Timecode_int']

            e1=f_n['n']

            Pop_nodes = self.graph.run("MATCH (n:Population_grid) where n.GeoSOT_string =~ \'"+f_mgcode+".*\' return n").data()
            e22=self.graph.run("MATCH (t:Time{Time_code:"+f_timecode+"}) return t").data()[0]['t']
            nodes = []
            rels = []
            nodes.append(e22)
            for pop_node in Pop_nodes:
                e2 = pop_node['n']

                #self.graph.create(rel)
                e11 = Node("People_trapped",count=e2['Population_count'])
                rel = Relationship(e11, 'caused_by', e1)
                nodes.append(e2)
                nodes.append(e11)
                rel1 = Relationship(e11, "has_influenced",e2)
                rel2 = Relationship(e11,'at_Time',e22)
                rels.append(rel)
                rels.append(rel1)
                rels.append(rel2)
                #self.graph.create(rel1)
                #self.graph.create(rel2)
            i=i+1
            print(i)
            subgraph = Subgraph(nodes, rels)
            tx = self.graph.begin()
            tx.create(subgraph)
            tx.commit()


    def create_Subway_relation(self):
        flood_grid_nodes = self.graph.run("MATCH (n:flood_grid) where n.Level=\"I\" or n.Level=\"II\" RETURN n").data()
        # nodes = []
        # rels = []
        i = 0
        for f_n in flood_grid_nodes:
            f_mgcode = f_n['n']['GeoSOT_string']
            f_timecode = f_n['n']['Timecode_int']
            e1 = f_n['n']
            Subway_nodes = self.graph.run(
                "MATCH (n:Subway_entry) where n.GeoSOT_string =~ \'" + f_mgcode + ".*\' return n").data()
            e22 = self.graph.run("MATCH (t:Time{Time_code:" + f_timecode + "}) return t").data()[0]['t']
            for subway_node in Subway_nodes:
                e2 = subway_node['n']

                e11 = Node("Subway_entry_flooded",flooded_depth=float(e1['Depth']))
                rel1 = Relationship(e11, "has_influenced", e2)
                rel2 = Relationship(e11, 'at_Time', e22)
                rel = Relationship(e11, 'caused_by', e1)
                self.graph.create(rel)
                self.graph.create(rel1)
                self.graph.create(rel2)
                i = i + 1
                print(i)

    def create_relation_flood(self):
        with open("./Test/flood_disnode_target_level.txt","r",encoding="utf-8") as f_flood:
            flood_lines = f_flood.readlines()
        with open("./Test/Building_simple.txt","r",encoding="utf-8") as f_building:
            building_lines = f_building.readlines()
        with open("./Test/Road_simple.txt", "r", encoding="utf-8") as f_road:
            road_lines = f_road.readlines()
        for line in flood_lines:
            flood_geosot = line.split("\t")[0]
            flood_geosot_group = eval(line.split("\t")[1].strip())
            nodes = []
            rels = []
            # for l1 in building_lines:
            #     building_geosot_group =eval(l1.split("\t")[1].strip())
            #     rel = spatial_relation_geosots_simple(flood_geosot_group,building_geosot_group)[1]
            #     if rel == "contains" or rel=="overlap":
            #         print(rel)
            #         build_No = l1.split("\t")[0]
            #         f_nodes = self.graph.run("MATCH (n:flood_grid{GeoSOT_string:\"" + flood_geosot + "\",Flood_level:\"I\"}) RETURN n").data()
            #
            #         e2 = self.graph.run("MATCH (n:Building) where n.Building_No=\"" + build_No + "\" RETURN n").data()[0]['n']
            #         nodes.append(e2)
            #         for f_node in f_nodes:
            #             f_timecode = f_node['n']['Timecode_int']
            #             e11 = Node("Building_flooded", flooded_depth=float(f_node['n']['Depth']))
            #             e22 = self.graph.run("MATCH (t:Time{Time_code:" + f_timecode + "}) return t").data()[0]['t']
            #             nodes.append(e11)
            #             nodes.append(e22)
            #             rel1 = Relationship(e11, "locate_at", e2)
            #             rel2 = Relationship(e11, 'at_Time', e22)
            #             rels.append(rel1)
            #             rels.append(rel2)
                    # Rel = Relationship(e1, rel, e2)
                    # self.graph.create(Rel)
            # if len(rels)!=0:
            #     subgraph = Subgraph(nodes, rels)
            #     tx = self.graph.begin()
            #     tx.create(subgraph)
            #     tx.commit()
            print("end 1!\n")
            nodes = []
            rels = []
            for l2 in road_lines:
                road_geosot_group = eval(l2.split("\t")[1].strip())
                rel = spatial_relation_geosots_simple(flood_geosot_group, road_geosot_group)[1]
                if rel == 'contains' or rel == 'overlap':
                    print(rel)
                    road_No = l2.split("\t")[0]
                    f_nodes = self.graph.run("MATCH (n:flood_grid{GeoSOT_string:\"" + flood_geosot + "\"}) RETURN n").data()
                    e2 = self.graph.run("MATCH (n:Road) where n.Road_No=\"" + road_No + "\" RETURN n").data()[0][
                        'n']
                    nodes.append(e2)
                    for f_node in f_nodes:
                        f_timecode = f_node['n']['Timecode_int']
                        e11 = Node("Road_flooded", flooded_depth=float(f_node['n']['Depth']))
                        e22 = self.graph.run("MATCH (t:Time{Time_code:" + f_timecode + "}) return t").data()[0]['t']
                        nodes.append(e11)
                        nodes.append(e22)
                        rel1 = Relationship(e11, "locate_at", e2)
                        rel2 = Relationship(e11, 'at_Time', e22)
                        rels.append(rel1)
                        rels.append(rel2)
            if len(rels) != 0:
                print("test!!!")
                print(len(rels))

                subgraph = Subgraph(nodes, rels)
                #nx.draw(subgraph)
                tx = self.graph.begin()
                tx.create(subgraph)
                tx.commit()
                # if rel=='contains' or rel=='overlap':
                #     e1 = self.graph.run("MATCH (n:flood_grid{GeoSOT_string:"+flood_geosot+"}) RETURN n").data()['n']
                #     e2 = self.graph.run("MATCH (n:Road) where n.GeoSOT_string_group=" + line.split("\t")[
                #         -1].strip() + " RETURN n").data()['n']
                #     Rel = Relationship(e1, rel, e2)
                #     self.graph.create(Rel)
            print("end 2!\n")
        f_flood.close()
        f_road.close()
        f_building.close()




if __name__ == '__main__':
    query = QueryforNeo4j()
    query.query_spatial_range()
    #query.query_temporal_range()

    #data_neo4j.create_relation()
    #data_neo4j.create_relation_flood()
    #data_neo4j.create_node()
    #data_neo4j.create_nodeandrelation()
    #data_neo4j.create_Subway_relation()

