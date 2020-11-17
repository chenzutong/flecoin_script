import json
import os
import sqlite3
from time import strftime, localtime
import time

conn = sqlite3.connect('data.db')
# 创建一个Cursor
cursor = conn.cursor()


if __name__ == '__main__':
    file_format = "iso"
    curated_dataset = "Linux ISO"
    price = "0.0000000005"
    duration = "600000"
    with open("./miner.json", "r") as f:
        miners = json.load(f)["miners"]

    res = cursor.execute('select * from local limit 0,{}'.format(str(len(miners))))
    index = 0
    data = []
    for r in res:
        data.append(r)

    while True:
        r = data[index]
        print(r)
        id = r[0]
        data_cid = r[1]
        deal_size_in_bytes = r[2]
        filename = r[3].split("/")[1]
        miner = miners[index]
        date = strftime("%Y-%m-%d %H:%M", localtime())
        index += 1
        print("lotus client deal {} {} {} {}".format(data_cid, miner, price, duration))
        deal_cid = os.popen("lotus client deal {} {} {} {}".format(data_cid, miner, price, duration)).read().split()[0]
        print(id, data_cid, deal_size_in_bytes, filename, miner, deal_cid, file_format, curated_dataset, date)
        cursor.execute("""
            insert into deal (
            id, data_cid, deal_size_in_bytes, filename, miner_id, deal_cid, file_format, curated_dataset, date)
            values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")
            """.format(id, data_cid, deal_size_in_bytes, filename, miner, deal_cid, file_format, curated_dataset, date))
        conn.commit()
        if index == len(miners):
            break
        time.sleep(60*20)

    # 关闭游标
    cursor.close()
    # 关闭Connection
    conn.close()