# -*- coding: utf-8 -*-
# 微博数据预处理.
import xlrd
import re
import numpy as np
import jionlp as jio
from datetime import datetime
import json
import emojiswitch
import Timecode

import clr
from ctypes import *

clr.AddReference('GeoSOT')
from GeoSOT import *
import morton
import Spatialcode
from wgs_bd_gd import *

def read_data():
    xl = xlrd.open_workbook("./Weibo_shanzhu.xlsx")
    table = xl.sheets()[0]
    print(table)
    rows = table.nrows
    print(rows)
    columns = table.ncols
    print(columns)
    col_txt = table.col_values(1)
    col_time = table.col_values(2)
    #col_lon = table.col_values(3)
    #col_lat = table.col_values(2)
    #col_loc = table.col_values(18)

    # for i in range(1,rows):
    #     # 获取txt内容（第三列）
    #     print(i, cols[i])
    return col_txt, col_time


def find_topic_and_name(content):
    topic_list = []
    name_list = []
    remove_list = []
    title_list = []
    for i in content:
        topic = re.findall('#[^#]+#', str(i))
        name = re.findall('@[\\u4e00-\\u9fa5\\w\\-]+', str(i))
        title = re.findall('[【][^【]+[】]', str(i))
        # print(title)
        topic_list.append(" ".join(topic))
        name_list.append(" ".join(name))
        title_list.append(" ".join(title))
        remove_topic = re.sub(r'#[^#]+#', "", str(i))
        remove_name = re.sub('@[\\u4e00-\\u9fa5\\w\\-]+', "", remove_topic)
        remove_title = re.sub('[【][^【]+[】]', "", remove_name)
        # remove_title = re.sub(r'\s+', " ", remove_title)  # 合并正文中过多的空格
        txt = jio.clean_text(remove_title)
        # 将全角字母数字空格替换为半角, 去除异常符号, 删除html标签，如 < span > 等, 删除冗余字符，如“\n\n\n”，修剪为“\n”, 删除括号及括号内内容，如“（记者：小丽）”, 删除 url 链接
        # 删除电话号码

        remove_list.append(txt.strip(" [，],:[：]").strip())

    return topic_list, name_list, title_list, remove_list

def clear_content(content):
    clear_list=[]
    for i in content:
        remove_topic = re.sub(r'#[^#]+#', "", str(i))
        # name = re.findall('@[\\u4e00-\\u9fa5\\w\\-]+', str(i))
        # print(name)
        remove_name = re.sub('@[\\u4e00-\\u9fa5\\w\\-]+', " ", remove_topic)
        remove_title = re.sub('[【][^【]+[】]', "", remove_name)
        remove_loc = re.sub('2[^0-9][\\u4e00-\\u9fa5\\w·\\-]+', "",remove_title)
        chinese_str = '视频'.encode('utf8').decode('utf8')
        #print(chinese_str)
        remove_video = re.sub('[\S]+'+chinese_str,"",remove_loc)

        print(remove_video)
        #remove_emoji = emojiswitch.demojize(remove_video,delimiters=("",""),lang="zh") # 将emoji表情转为中文文字
        txt = jio.clean_text(remove_video)
        #txt = jio.clean_text(remove_emoji)    # clean_text 将全角字母数字空格替换为半角, 去除异常符号, 删除html标签，如 < span > 等, 删除冗余字符，如“\n\n\n”，修剪为“\n”, 删除括号及括号内内容，如“（记者：小丽）”, 删除 url 链接
        # 删除电话号码
        # print(txt)
        txt_simple = jio.tra2sim(txt,mode='char')   # 繁体转简体，char 模式是按照字符逐个替换为简体字
        #print(txt_simple)                           # word 模式是将港台地区的词汇表述习惯，替换为符合大陆表述习惯的相应词汇，采用前向最大匹配的方式执行
        # remove_emoji = emoji.demojize(txt_simple)
        # print(remove_emoji)

        final_txt = txt_simple.replace(" ","")
        print(final_txt)
        print("\n")
        # clear_list.append(remove_emoji)
        clear_list.append(final_txt)
    return clear_list



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    txt_list, issue_time_list= read_data()  # 微博文本内容，发文时间，经度，纬度，地址
    print(txt_list)
    clear_list = clear_content(txt_list)
    #print(clear_content(txt_list))
    # topic_list, name_list, title_list, remove_list = find_topic_and_name(txt_list)
    issue_time_list_final=[]
    for i in range(1, len(issue_time_list)):
        #t1 = issue_time_list[i].replace('\n', '').replace('\r','').replace(' ','')
        #print(i,t1)
        t1 = issue_time_list[i]
        #time = jio.ner.extract_time(t1, with_parsing=False)[0]   # 提取第一个用户发文时间，暂不考虑转发用户的发文时间
        # print(i)
        t2 = datetime.strptime(t1,'%Y年%m月%d日 %H:%M')   #字符串（e.g.2015年12月20日11：40）转为datetime
        #t2 = xlrd.xldate.xldate_as_datetime(t1,0)
        #t2 = datetime.strptime(t1, '%Y\/%m\/%d %H:%M')
        issue_time_list_final.append(t2)
    np.savez_compressed('./Preprocessed_weibo.npz',
                        txts=clear_list[1:], base_times=issue_time_list_final)
    with open('Weibo_shanzhu_preprocessed.txt','w',encoding='utf-8') as f1:
        for i in range(1,len(clear_list)):
            json.dump(clear_list[i],f1,ensure_ascii=False)
            f1.write("\n")
    Preprocessed_data = np.load('./Preprocessed_weibo.npz', allow_pickle=True)
    processed_txt = Preprocessed_data["txts"]
    base_times = Preprocessed_data["base_times"]

    # checkin_lons = Preprocessed_data["lons"]
    # checkin_lats = Preprocessed_data["lats"]
    # level =19
    # with open('Checkin_Spatial_code','w',encoding='utf-8') as fout:
    #     for lon, lat in zip(checkin_lons, checkin_lats):
    #         wgs_lon,wgs_lat=gcj02_to_wgs84(lon,lat)
    #
    #         _tile = Tile(float(wgs_lon), float(wgs_lat), level)
    #         Mgcode = Spatialcode.get_Spatialcode(_tile.gcode,level)
    #         fout.write(_tile.ToString()+"\t"+str(Mgcode)+"\n")


    timestr2codelevel = [5,9,14,19,25,31]

    with open('./Weibo_shanzhu_time.txt', 'w', encoding='utf-8') as f2:
        for i in range(len(processed_txt)):
            print(i, processed_txt[i])
            times = []
            time_set = jio.ner.extract_time(processed_txt[i], with_parsing=False) # 提取时间实体，先不进行时间语义解析
            for time_str in time_set:
                t = {}
                t["text"] = time_str["text"]
                t["type"] = time_str["type"]
                times.append(t)

            json.dump(times, f2, ensure_ascii=False)
            f2.write("\n")
    Timecode_list = []
    with open('./Weibo_time_解析后.txt', 'w', encoding='utf-8') as f3, open('./Weibo_shanzhu_time_修正.txt', 'r', encoding='utf-8') as f4, open(
            './Weibo_time_解析后_时间编码.txt', 'w', encoding='utf-8') as f5:
        i = 0
        for line in f4.readlines():
            time_set1 = json.loads(line)
            # print(i, time_set1)
            time_parse_time = []
            time_parse_MTcode = []
            j=0
            for time_entity in time_set1:
                # if re.match('[第]\S+[天]', time_entity['text']):
                #     base_time = datetime(2015,12,20)
                # elif re.match('\d[个]*[小时]', time_entity['text']):
                #     base_time = datetime(2015,12,20,11,40)
                # else:
                #     base_time = base_times[i]
                base_time = base_times[i]
                pair_MTcode = []
                try:
                    t = jio.parse_time(time_entity['text'], time_type=time_entity['type'], time_base=base_time)
                    print(i, t["full_time"])
                    full_time = t["full_time"]
                    first_time = full_time[0]
                    # print(first_time)
                    idx = 0
                    for s in first_time:
                        if s < 0 or idx==6:
                            break
                        else:
                            idx=idx+1
                    #index1 = first_time.index(-1)
                    index1 = idx-1
                    level1= timestr2codelevel[index1]
                    first_time_str = t["time"][0]
                    first_time = Timecode.get_Timesegments(first_time_str)
                    first_time_code = Timecode.get_Timecode(first_time,level1)
                    pair_MTcode.append(first_time_code)
                    #print(first_time_code)
                    second_time = full_time[1]
                    idx = 0
                    for s in second_time:
                        if s < 0 or idx==6:
                            break
                        else:
                            idx = idx + 1
                    index2 = idx-1
                    level2 = timestr2codelevel[index2]
                    second_time_str = t["time"][1]
                    second_time = Timecode.get_Timesegments(second_time_str)
                    second_time_code = Timecode.get_Timecode(second_time, level2)
                    pair_MTcode.append(second_time_code)
                    pair_MTcode.append((i,j))
                    j=j+1
                    #print(second_time_code)
                    #index2 = second_time.index(-1)
                    #print(timestr2codelevel[index2])


                except Exception:
                    t = 'error'
                time_parse_time.append(t)
                time_parse_MTcode.append(pair_MTcode)
                if len(pair_MTcode)!=0:
                    Timecode_list.append(pair_MTcode)
            json.dump(time_parse_time,f3, ensure_ascii= False)
            f3.write("\n")
            json.dump(time_parse_MTcode, f5, ensure_ascii=False)
            f5.write("\n")
            i = i + 1
        print(Timecode_list)
        print(len(Timecode_list))
        count=0
        for i in range(0,len(Timecode_list)-1):
            for j in range(i+1,len(Timecode_list)):
                count=count+1
                print(Timecode.get_temporal_relation(Timecode_list[i],Timecode_list[j]))
        print(count)

    # with open('Weibo_time_解析后_时间编码.txt', 'r', encoding='utf-8') as f5:
    #

            #print(times)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
