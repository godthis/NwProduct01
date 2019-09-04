import copy
import http
import itertools
import os
import re
import time

import tkinter
import urllib
from tkinter import *

import requests
import xlsxwriter as xlsxwriter
import xlwt as xlwt

if os.path.exists(r'C:\temp\a.xlsx'):
    os.remove(r'C:\temp\a.xlsx')

workbook = xlsxwriter.Workbook(r'C:\temp\a.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, '商品货号')
worksheet.write(1, 0, 'test200190904003')
workbook.close()




useranme = 'BL0001'
password = 'qs8888'
from untils.searchDB import searchmysql
def loginandgetcookie():
    cookie = http.cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(handler)
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Accept':'application/json, text/plain, */*','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'} # 设置请求头

    url = 'http://issx.bl.test2.qs.com/ISSX/login/login'
    values = 'username=%s&password=%s' % (useranme, password)
    request = urllib.request.Request(url=url, headers=headers, data=values.encode(encoding='UTF8')) # 需要通过encode设置编码 要不会报错
    # 发送请求
    #response = urllib.request.urlopen(request)
    response = opener.open(request)
    #调整下cookie，感觉有点儿蠢
    for item in cookie:
        cookievalue = str(item.name) +'='+ str(item.value)
    return cookievalue


url = 'http://issx.bl.test2.qs.com/ISSX/spPartGoods/importExcel'
files = {'upload': ('a.xlsx', open(r'C:\temp\a.xlsx', 'rb'), 'application/octet-application/vnd.openxmlformats-officedocument.spreadsheetml.sheetstream')}
headers = {'Accept':'application/json, text/plain, */*',
           'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
           # 'Content-Type':'multipart/form-data;',
           'Cookie':loginandgetcookie()}
data = {'uploadFileName':'a.xlsx','uploadContentType':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','buscontsId':'10042003'}
response = requests.post(url, files=files, headers=headers, data=data)
resp = response.text
print(resp)



'''
a = '100.10'

b = '20'

c = float(b) * float(a)
print(c)

# 2019-9-3 18:28:47

root = tkinter.Tk()



def checknum(content):
    if content.isdigit() or (content ==""):
        return True
    else:
        return False

v = tkinter.StringVar()
testCMD=root.register(checknum)
entrytest = tkinter.Entry(root, textvariable = v, validate = 'key', validatecommand=(testCMD, '%P'))

entrytest.pack()
mainloop()


'''

'''
sizegroupid =1000070
sizeidlist = searchmysql(
            "select size_id from qs_iss_mas.pti_size_group_dt where own_company_id = 562 and size_group_hd_id = '%s';" % sizegroupid,
            "(.*)?")
sizeidlist = re.findall("(?<=[(])[0-9]+(?=,[)])", sizeidlist)
# 获取每个尺码id对应的尺码code和尺码name
sizecodelist = [''] * len(sizeidlist)
sizenamelist = [''] * len(sizeidlist)
for i in range(len(sizeidlist)):
    sizetmp = searchmysql(
        "select size_code,size_name from qs_iss_mas.pti_size where own_company_id = 562 and id = '%s';" % sizeidlist[i],
        "(.*)?")
    sizecodelist[i] = re.search("(?<=[(]')(.*?)(?=',)", sizetmp).group()
    sizenamelist[i] = re.search("(?<= ')(.*?)(?='[)])", sizetmp).group()


# 颜色名称列表
colornamelist = re.findall("(?<=')[^,].*?(?=')", "['白色','通用']")
# 获取颜色id和颜色code
coloridlist=['']*len(colornamelist)
colorcodelist=['']*len(colornamelist)
for i in range(len(colornamelist)):
    # 获取颜色id
    colortmp = searchmysql(
        "select id, color_code from qs_iss_mas.pti_color where own_company_id = 562 and color_name = '%s';" % colornamelist[i],
        "(.*)?")
    coloridlist[i] = re.search("(?<=[(][(])(.*?)(?=,)", colortmp).group()
    colorcodelist[i] = re.search("(?<= ')(.*?)(?='[)])", colortmp).group()





pid = '260059'
skulist=[]
for coli in range(len(coloridlist)):
    for sizei in range(len(sizeidlist)):
        tmp=['']*7
        tmp[1] = sizeidlist[sizei]
        tmp[2] = sizecodelist[sizei]
        tmp[3] = sizenamelist[sizei]
        tmp[4] = coloridlist[coli]
        tmp[5] = colorcodelist[coli]
        tmp[6] = colornamelist[coli]

        sql = "select id from qs_iss_mas.pti_part_dt_sku where own_company_id = 562 and eff_flag = 1 and pti_part_hd_id = '%s' and size_id = '%s' and color_id = '%s';" % (
        pid, sizeidlist[sizei], coloridlist[coli])
        #print(sql)
        skudttmp = searchmysql(sql, "(.*)?")
        skudttmp = re.search("(?<=[(][(]).*?(?=,[)])", skudttmp).group()
        #tmp[0] = skudttmp
        skulist.append(copy.deepcopy(tmp))


ptiPartDtSkuDtos = ''
print(skulist)
firstflag = True
colortmp = itertools.groupby([skutmp[4:7] for skutmp in skulist])
for colorlist, i in colortmp:
    if firstflag == True:
        firstflag = False
    else:
        ptiPartDtSkuDtos = ptiPartDtSkuDtos + ','
    ptiPartDtSkuDtos = ptiPartDtSkuDtos + '{"colorId":' + colorlist[0] + ',"colorCode":"' + colorlist[1] \
                       + '","colorName":"' + colorlist[2] + '","deleteFlag":0}'
print(ptiPartDtSkuDtos)
'''
"""
#print(coloridlist[coli])
#print(sizeidlist[sizei])
sql = "select id from qs_iss_mas.pti_part_dt_sku where own_company_id = 562 and eff_flag = 1 and pti_part_hd_id = '%s' and size_id = '%s' and color_id = '%s';" % (pid, sizeidlist[sizei], coloridlist[coli])
print(sql)
ptiparthddtskuidtmp = searchmysql(sql, "(.*)?")
ptiparthddtskuidtmp = searchmysql(sql, "(.*)?")
ptiparthddtskuidtmp = re.search("(?<=[(][(]).*?(?=,[)])", ptiparthddtskuidtmp).group()
print(ptiparthddtskuidtmp)
ptiparthddtskuidlist[sizei][coli] = ptiparthddtskuidtmp
"""


