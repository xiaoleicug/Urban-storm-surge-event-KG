import requests

import time


def get_mercator(addr):
    url='http://api.map.baidu.com/geocoding/v3/?address=%s&city=深圳市&ret_coordtype=gcj02ll&output=json&ak=Aed5oTiEj7o3wQ2OkicgjxAVai12m1iG&callback=showLocation' %(addr)
    response = requests.get(url)
    return response.text


def writeline(src, dest):
    count = 0
    ms = open(src, encoding='utf-8')
    num = ms.readlines()
    print(len(num))
    print("-------------------")

    for line in num:
        with open(dest, "a", encoding='utf-8') as mon:
            loc = get_mercator(line)
            print(loc)

            mon.writelines(loc)

            mon.write("\n")

            time.sleep(0.1)

            count += 1

            print("第" + str(count) + "条数据写入成功...")

writeline(r"这里是你的原始数据路径", r"这里是你的数据输出路径")