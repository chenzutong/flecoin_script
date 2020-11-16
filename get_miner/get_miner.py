import requests
from bs4 import BeautifulSoup
import xlwt
import string
from time import strftime, localtime


all_str = string.ascii_letters + string.digits
excelpath =('./矿工钱包跟踪{}.xls'.format(strftime("%m-%d", localtime())))  #新建excel文件
workbook = xlwt.Workbook(encoding='utf-8')  #写入excel文件
sheet = workbook.add_sheet('Sheet1',cell_overwrite_ok=True)  #新增一个sheet工作表

# 添加表头
headlist=[u'排名',u'矿工号',u'标签',u'算力',u'24H出块奖励(FIL)',u'24H增加',u'矿工额度(FIL)',u'Onwer地址',u'Onwer额度(FIL)',u'Worker地址',u'Worker额度(FIL)']   #写入数据头
row=0
col=0
for head in headlist:
    sheet.write(row,col,head)
    col=col+1
workbook.save(excelpath) #保存

# 爬取filfox网站信息
headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'}
index = "https://filfox.info/zh/ranks/power"
response = requests.post(index,headers=headers)
html_doc = response.text
soup = BeautifulSoup(html_doc, features="lxml")
miner_list = soup.find_all('tr', class_='border-b border-background h-10')[:20]
filfox_url = "https://filfox.info/zh/address/"
for v,i in enumerate(miner_list):
    id = str(v+1)
    data = []
    increase = i.find_all('td')[6].string
    reward = i.find_all('td')[4].string.split(".")[0]
    power = i.find_all('div', class_='flex items-center justify-start')[0].find_all('div')[4].string
    name = i.find_all('div')[1].string
    miner = i.find_all('a')[0].string
    print(miner)

    url = "{}{}".format(filfox_url, miner)
    response = requests.post(url,headers=headers)
    html_doc = response.text
    soup = BeautifulSoup(html_doc, features="lxml")
    print(soup.find_all('p', class_="font-medium text-2xl")[0].string.strip())
    miner_bal = soup.find_all('p', class_="font-medium text-2xl")[0].string.strip().split(".")[0]
    owner = soup.find_all('a')[28].attrs["href"].split("/")[3]
    print(soup.find_all('a')[28].attrs["href"].split("/")[3])
    worker = soup.find_all('a')[29].attrs["href"].split("/")[3]
    print(soup.find_all('a')[29].attrs["href"].split("/")[3])

    # onwer
    url = "{}{}".format(filfox_url, owner)
    response = requests.post(url,headers=headers)
    html_doc = response.text
    soup = BeautifulSoup(html_doc, features="lxml")
    print(soup.find_all('dd', class_='mr-4')[3].string.strip())
    owner_bal = soup.find_all('dd', class_='mr-4')[3].string.strip().split(".")[0]


    # worker
    url = "{}{}".format(filfox_url, worker)
    response = requests.post(url,headers=headers)
    html_doc = response.text
    soup = BeautifulSoup(html_doc, features="lxml")
    print(soup.find_all('dd', class_='mr-4')[3].string.strip())
    worker_bal = soup.find_all('dd', class_='mr-4')[3].string.strip().split(".")[0]

    # 写入excel
    data.append(id)
    data.append(miner)
    data.append(name)
    data.append(power)
    data.append(reward)
    data.append(increase)
    data.append(miner_bal)
    data.append(owner)
    data.append(owner_bal)
    data.append(worker)
    data.append(worker_bal)
    for j in range(len(data)):
        sheet.write(v+1, j, data[j])

    workbook.save(excelpath)  # 保存
    print("-"*100)
