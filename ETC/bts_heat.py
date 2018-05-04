# encode:utf-8
import urllib2
import json
from pymongo import MongoClient

from StringIO import StringIO
import gzip
from urllib import quote_plus

uri = "mongodb://%s:%s@%s" % (quote_plus('用户名'), quote_plus('密码'), 'ip:port')
dbClient  = MongoClient(uri)
dbname = "数据库名"
db = dbClient[dbname]
coll_bts = db["bts_heat"]

centerLon = 116.360766121 + 0.001683379
centerLat = 39.9257293 - 0.0004633

lengthLat = 0.000105
lengthLon = 0.0000979

startTime = "2018-02-22+00:00:00"
endTime = "2018-02-22+23:30:00"
startDate = "2018-02-22"
endDate = "2018-02-23"

cook = "RK=kSmOaYhKO2; pgv_pvi=464429056; tvfe_boss_uuid=5456f579e197e5e1; ts_uid=2099138638; ptcz=2ae40440b21214a011eee8b51760f549684da24bb8a6937188465a1df09c771e; pt2gguin=o0947997167; pgv_pvid=5707612398; o_cookie=947997167; pac_uid=1_947997167; PHPSESSID=r466qh981gnoujs2c6jbhi1b76; pgv_info=ssid=s5181698692; ts_last=heat.qq.com/zone/show.php; suid=7295140288; current_prov_name=%E5%8C%97%E4%BA%AC%E5%B8%82; current_city_name=%E5%8C%97%E4%BA%AC%E5%B8%82; current_region_name=; current_region_id=null"

url = r'https://heat.qq.com/api/getPopulationByDateTime.php?sub_domain=zone&time_begin=' + startTime +r'&region_id=7737&time_end='+ endTime +r'&range=30'
url2 = r'https://heat.qq.com/api/getLocation_uv_lbs.php?region_id=7737&date_begin=' + startDate + '&date_end=' + endDate + '&range=30&predict=false&sub_domain=zone'

header = {
        "Accept-Encoding":"gzip, deflate, br",
        "Connection":"keep-alive",
        "Host":"heat.qq.com",
        "Cookie":cook
        }

    

request = urllib2.Request(url,headers=header)

response = urllib2.urlopen(request)

content = ""
encoding = response.headers["content-encoding"]
if encoding == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    content = f.read()
else:
    content = response.read()

jsonFile = json.loads(content)
data = jsonFile["data"]



request = urllib2.Request(url2,headers=header)
response = urllib2.urlopen(request)

content = ""
encoding = response.headers["content-encoding"]
if encoding == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    content = f.read()
else:
    content = response.read()
jsonFile2 = json.loads(content)
data2 = jsonFile2["data"]
data2 = data2[startDate]

i = 0
for item in data:
    item["lbs"] = data2[i]
    i += 1
    tm = item["tm"]
    tm = tm.replace(" ","+")
    url3 = r'https://heat.qq.com/api/getHeatDataByTime.php?region_id=7737&datetime=' + tm + '&sub_domain=zone'

    request = urllib2.Request(url3,headers=header)

    response = urllib2.urlopen(request)
    content = ""
    encoding = response.headers["content-encoding"]
    if encoding == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        content = f.read()
    else:
        content = response.read()

    jsonFile = json.loads(content)
    list = []
    for key in jsonFile:
        if jsonFile[key] == 0:
            continue
        keyTemp = key.split(",")
        lon = centerLon + float(keyTemp[1]) * lengthLon
        lat = centerLat + float(keyTemp[0]) * lengthLat
        value = jsonFile[key]
        list.append({"lon":lon,"lat":lat,"value":value})


    item["heat"] = list
    
    coll_bts.insert(item)







 
