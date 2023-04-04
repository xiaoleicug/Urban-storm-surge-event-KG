import math
from datetime import datetime


def get_Timesegments(time_str):
    list = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    # print(list)

    return list



def get_Timecode(time_list, level):
    m = 32
    Tc = (time_list.year - 1990) << 26 | time_list.month << 22 | time_list.day << 17 | time_list.hour << 12 | time_list.minute << 6 | time_list.second
    # return bin(code>>(31-level))[2:]
    # print(Tc)
    Tc0 = Tc << 1
    DetaT = (1 << (m - level - 1)) - 1
    MTc = ((Tc0 >> (m - level)) << (m - level)) + DetaT
    # print(MTc)

    return MTc

def get_level(MTc):
    m = 32
    n = 5
    level = 0
    if MTc & 1 == 0:
        level = m - 1
    else:
        Mid = (MTc - 1) ^ (MTc + 1)
        # print(bin(Mid))
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
    return level

def convertcode2str(MTc):
    m = 32
    level = get_level(MTc)
    Tc = (MTc - (1 << (m - level - 1)) + 1) >> 1
    Tc_str = list(bin(Tc))
    print(bin(Tc))
    year = 1990 + (Tc >> 26)
    month = (Tc >> 22) & (0b1111)
    day = (Tc >> 17) & (0b11111)
    hour = (Tc >> 12) & (0b11111)
    minute = (Tc >> 6) & (0b111111)
    second = Tc & (0b111111)

    if level <= 5:
        time_str = str(year)
    elif level <= 9:
        time_str = str(year) + "年" + str(month)+ "月"
    elif level <= 14:
        time_str = str(year) + "年" + str(month) + "月" + str(day)+ "日"
    elif level <= 19:
        time_str = str(year) + "年" + str(month) + "月" + str(day)+ "日" +  str(hour)+ "时"
    elif level <= 25:
        time_str = str(year) + "年" + str(month) + "月" + str(day)+ "日" + str(hour) + "时" + str(minute)+"分"
    else:
        time_str = str(year) + "年" + str(month) + "月" + str(day)+ "日"+  str(hour) + "时" + str(minute)+"分" + str(
            second)+"秒"

    return time_str

# 按照 剖分时间编码段的编码二叉树结构来计算
def get_Timecode_containment(MTc):
    m = 32
    level = get_level(MTc)
    A = MTc-(1<<(m-level-1))+1
    B = MTc+(1<<(m-level-1))-1
    return (A,B)

def get_Timecode_inclusion(MTc,N1):
    m =32
    level = get_level(MTc)
    OTn = (1<<(m-1-level+N1))-1
    print(OTn)
    FTc =((MTc>>(m-level+N1))<<(m-level+N1))+OTn
    return FTc


def get_temporal_relation(MTc1, MTc2):
    (a1, b1) = get_Timecode_containment(MTc1[0])
    (a2, b2) = get_Timecode_containment(MTc1[1])
    relation_pair =-1
    if a2 < b1 and a2!=a1:
        print("1 error")
        return 0

    A1 = a1
    B1 = b2
    (a1, b1) = get_Timecode_containment(MTc2[0])
    (a2, b2) = get_Timecode_containment(MTc2[1])
    if a2 < b1 and a2!=a1:
        print("2 error")
        return 0
    A2 = a1
    B2 = b2
    if B1 < A2:
        r = "相离"
        relation_pair = (MTc1[2], r, MTc2[2])
    if B2 < A1:
        r = "相离"
        relation_pair = (MTc2[2], r, MTc1[2])
    if A1 <= A2 and B2 <= B1:
        r = "包含"
        relation_pair = (MTc1[2], r, MTc2[2])
    if A1 >= A2 and B2 >= B1:
        r = "包含"
        relation_pair = (MTc2[2], r, MTc1[2])
    if A1 < A2 and A2 < B1 and B1 < B2:
        r = "相交"
        relation_pair = (MTc1[2], r, MTc2[2])
    if A1 > A2 and A1 < B2 and B2 < B1:
        r = "相交"
        relation_pair = (MTc2[2], r, MTc2[2])
    if A1 == B2 + 2:
        r = "相接"
        relation_pair = (MTc2[2], r, MTc1[2])
    if A2 == B1 + 2:
        r = "相接"
        relation_pair = (MTc1[2], r, MTc2[2])
    return relation_pair





if __name__ == "__main__":
    l = get_Timesegments("2018-09-16 19:20:00")
    level = 19
    time_code = get_Timecode(l, level)
    print(time_code)
    # # print(len(bin(time_code)))
    # print(get_level(time_code))
    time_code=3837906943
    print(convertcode2str(time_code))
    # print(get_Timecode_containment(time_code))
    # Containments = get_Timecode_containment(time_code)
    # A= convertcode2str(Containments[0])
    # B = convertcode2str(Containments[1])
    # print(A)
    # print(B)
    # print(get_level(Containments[0])) # 31
    # print(get_level(Containments[1])) # 26
    # print(get_Timecode_inclusion(time_code,6))
    # l1 = get_Timesegments("2015-12-24 12:16:00")
    # l2 = get_Timesegments("2015-12-24 12:17:00")
    # mtc1 = []
    # mtc1.append(get_Timecode(l1, level))
    # mtc1.append(get_Timecode(l2, level))
    # mtc2 = []
    # l3 = get_Timesegments("2015-12-24 12:18:00")
    # l4 = get_Timesegments("2015-12-25 10:18:00")
    # mtc2.append(get_Timecode(l3, 25))
    # mtc2.append(get_Timecode(l4, 25))
    # print(mtc2)
    # print(get_temporal_relation(mtc1,mtc2))
    # mtc1=[3837867711, 3837867711,"mtc1"]
    # mtc2=[3837882367, 3837882367,"mtc2"]
    # mtc3=[3837698239, 3837698239,"mtc3"]
    # mtc4=[3837841407, 3837865983,"mtc4"]
    # print(get_temporal_relation(mtc1,mtc2))
    # print(get_temporal_relation(mtc2, mtc3))
    # print(get_temporal_relation(mtc1, mtc3))
    # print(get_temporal_relation(mtc3, mtc4))
    # print(get_temporal_relation(mtc1, mtc4))
    # print(get_temporal_relation(mtc2, mtc4))


    # print(len(bin(get_Timecode(list,30))))
