import os
import sqlite3

isData = os.path.exists('./data.db')

# 连接到SQLite数据库
# 数据库文件是data.db，如果文件不存在，会自动在当前目录创建
conn = sqlite3.connect('data.db')

# 创建一个Cursor
cursor = conn.cursor()

if isData == False:
    # 执行SQL语句，创建表
    cursor.execute("""
        create table local(id int(10) primary key, 
        data_cid varchar(200), 
        size varchar(200),
        filename varchar(200))""")
    cursor.execute("""
        create table deal(id int(10) primary key, 
        deal_cid varchar(200),
        deal_id varchar(200),
        filename varchar(200),
        peace_id varchar(200),
        data_cid varchar(200), 
        miner_id varchar(200), 
        file_format varchar(200), 
        deal_size_in_bytes varchar(200), 
        size_deal varchar(200), 
        date varchar(200),
        curated_dataset varchar(200))""")


if __name__ == '__main__':
    names = ["10.04.0", "10.04.1", "10.04.2", "10.04.3", "10.04.4", "10.10"]
    for name in names:
        pwd = "/data/linux/releases/{}".format(name)
        command = "ls -l {} | grep iso".format(pwd)
        linux_list = os.popen("{}".format(command)).read().split("\n")[:-1]

        for l in linux_list:
            size = l.split()[4]
            n = l.split()[8]
            filename = "{}/{}".format(name, l.split()[8])
            res = os.popen("lotus client import {}/{}".format(pwd, n)).read().split()
            print(res)
            data_cid = res[3]
            id = res[1].split(",")[0]
            print(id, data_cid, size, filename)
            cursor.execute('insert into local (id, data_cid, size, filename) values ("{}", "{}", "{}", "{}")'.format(id, data_cid, size, filename))
            conn.commit()

    # 关闭游标
    cursor.close()
    # 关闭Connection
    conn.close()
