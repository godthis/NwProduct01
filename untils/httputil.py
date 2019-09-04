import http.cookiejar
import re
import urllib.request

import requests

useranme = 'BL0001'
password = 'qs8888'

#登录后台并获取cookie
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

def httppost(url,data):
    headers = {'Accept':'application/json, text/plain, */*', 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        , 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Cookie':loginandgetcookie()}
    request = urllib.request.Request(url=url, headers=headers, data=data.encode(encoding='UTF8'))
    response = urllib.request.urlopen(request)
    # logInfo = response.read().decode()
    resutlt = re.search('(?=\"code\").*?(?=,)', response.read().decode()).group()
    print("创建结果" + resutlt)

def httpget(url):
    headers = {'Accept': 'application/json, text/plain, */*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        , 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Cookie': loginandgetcookie()}
    request = urllib.request.Request(url=url, headers=headers,data=None)
    response = urllib.request.urlopen(request)
    # logInfo = response.read().decode()
    resutlt = re.search('(?=\"code\").*?(?=,)', response.read().decode()).group()
    print("创建结果" + resutlt)

def httpupload(url, fpath, buscontsId):

    files = {'upload': ('a.xlsx', open(fpath, 'rb'),
                        'application/octet-application/vnd.openxmlformats-officedocument.spreadsheetml.sheetstream')}
    headers = {'Accept': 'application/json, text/plain, */*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
               # 'Content-Type':'multipart/form-data;',
               'Cookie': loginandgetcookie()}
    data = {'uploadFileName': 'a.xlsx',
            'uploadContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'buscontsId': '%s' % buscontsId}
    response = requests.post(url, files=files, headers=headers, data=data)
    resp = response.text
    print(resp)