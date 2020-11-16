import os,time
from time import strftime, localtime


if __name__ == '__main__':
    while True:
        inf = os.popen("lotus-miner info").read()

        # 判断矿工进程是否启动，如果未启动直接退出
        if inf.find("ERROR") > -1:
            print(inf)
            break

        # 显示info列表
        info = inf.split("Sectors:")
        listnum = info[1].strip().split()
        dictnum = dict(zip(listnum[::2],listnum[1::2]))
        print(dictnum)

        # 显示时间
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()))

        # 显示正在运行sectors的数量
        total = int(dictnum.get("Total:"))
        proving = int(dictnum.get("Proving:"))
        removed = int(dictnum.get("Removed:"))
        run_sum = total - proving - removed
        print("The sectors running now is : " + str(run_sum))

        # 显示链接的worker数量
        worker_str = os.popen("echo \"$(lotus-miner sealing workers|wc -l)/5-1\" | bc").read().strip()
        print("Your number of workers is : " + worker_str)

        # 显示设置最大封存的sectors数量
        worker_num = int(worker_str)
        print("You set maximum running sector to : " + str(worker_num))

        if worker_num == 0:
            print("You didn't activate the Worker")
            break

        # 运行情况
#        if run_sum == 0:
#            os.popen("lotus-miner sectors pledge")
#            print("RUN: lotus-miner sectors pledge")

        if run_sum < worker_num:
            is_waitdeal = dictnum.get("WaitDeals:")
            if not is_waitdeal:
                os.popen("lotus-miner sectors pledge")
                print("RUN: lotus-miner sectors pledge")
            else:
                dealnum = os.popen("lotus-miner sectors list | grep WaitDeals").read().strip().split()[0]
                os.popen("lotus-miner sectors seal {}".format(dealnum))
                print("RUN: lotus-miner sectors seal {}".format(dealnum))

        if run_sum == worker_num:
            is_waitdeal = dictnum.get("WaitDeals:")
            if is_waitdeal:
                dealnum = os.popen("lotus-miner sectors list | grep WaitDeal").read().strip().split()[0]
                os.popen("lotus-miner sectors seal {}".format(dealnum))
                print("RUN: lotus-miner sectors seal {}".format(dealnum))

        print("Wait 20 minutes ...")
        print("-" * 100 + "\n")
        time.sleep(60 * 20)

        
