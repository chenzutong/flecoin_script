import json
import os
import time
import paramiko
import threading


class Monitor:
    def __init__(self, ip, user, passwd):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.ip = ip
        self.user = user
        self.passwd = passwd

    def connect(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 设置ssh连接超时时间20s
        self.client.connect(timeout=20, hostname=self.ip, port=22, username=self.user, password=self.passwd)

    def run_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        error = stderr.read().decode("utf-8")
        message = stdout.read().decode('utf-8')
        return error, message

    def close(self):
        self.client.close()


isFirst = True
lock = threading.Lock()


def loop(ip, ssh):
    try:
        ssh.connect()
    except Exception as e:
        print("{}连接ssh出错:".format(ip), e)
    else:
        err, mes = ssh.run_command(cmd)
        if err:
            mes = err
            print("error is : ", err)
        now = time.strftime("  %Y/%m/%d %H:%M:%S", time.localtime())
        line = "-"*100
        # 获取锁:
        lock.acquire()
        global isFirst
        if isFirst:
            with open("./log.txt", "w", encoding="utf-8") as f2:
                f2.write(ip + now + "\n" + mes + line + "\n\n")
            isFirst = False
        else:
            with open("./log.txt", "a", encoding="utf-8") as f2:
                f2.write(ip + now + "\n" + mes + line + "\n\n")
        # 释放锁:
        lock.release()
        ssh.close()


if __name__ == '__main__':
    # 读取配置文件
    with open("./machine.json", 'r') as load_f:
        load_dict = json.load(load_f)

    cmd = load_dict["cmd"]
    # 写入输出文件
    for ip in load_dict["ip"]:
        print(ip)
        ssh = Monitor(ip, load_dict["name"], load_dict["password"])
        t = threading.Thread(target=loop, args=(ip, ssh,))
        t.start()
