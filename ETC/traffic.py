# -- coding: utf-8 --
from pymongo import MongoClient
from urllib import quote_plus
import urllib2
import json
import datetime
# utf8编码问题
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# 分析的网页为: http://jiaotong.baidu.com/top/report/?citycode=131

# mongo连接
uri = "mongodb://%s:%s@%s" % (quote_plus('用户名'), quote_plus('密码'), 'ip:port')
dbClient  = MongoClient(uri)
dbname = "数据库名"
db = dbClient[dbname]
coll_traffic = db["traffic"]
coll_traffic_coefficient = db["traffic_coefficient"]
coll_traffic_mileage = db["traffic_mileage"]
coll_rushTime_mileage = db["traffic_rushtime"]
nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')

# top10拥堵路段名
topRoadUrl = "http://jiaotong.baidu.com/trafficindex/city/roadrank?cityCode=131&roadtype=0"
request = urllib2.Request(topRoadUrl)
response = urllib2.urlopen(request)
topJsonFile = json.loads(response.read())
roadList = topJsonFile["data"]["list"]
roadIdList = []
roadNameList = []
for roadItem in roadList:
    roadIdList.append(roadItem["roadsegid"])
    roadNameList.append(roadItem["roadname"])

# 每个路段的24h情况
roadDetailUrl = "http://jiaotong.baidu.com/trafficindex/city/roadcurve?cityCode=131&id="
for roadIndex in range(len(roadIdList)):
    detailTemp = roadDetailUrl + roadIdList[roadIndex]
    request = urllib2.Request(detailTemp.encode("utf-8"))
    response = urllib2.urlopen(request)
    roadJsonFile = json.loads(response.read())
    # 处理路段坐标
    location = roadJsonFile["data"]["location"]
    locationString = ""
    for locationItem in location:
        locationString += "," + locationItem
    locationString = locationString[1:]
    locationString = locationString.split(",")
    lon = [float(locationString[0])]
    lat = [float(locationString[1])]
    i = 2
    while i < len(locationString):
        lonTemp = float(locationString[i])
        latTemp = float(locationString[i + 1])
        if lonTemp != lon[len(lon) - 1] and latTemp != lat[len(lat) - 1]:
            lon.append(lonTemp)
            lat.append(latTemp)
        i += 2
    # 处理过去24小时时速和拥堵系数
    speed = []
    coefficient = []
    curve = roadJsonFile["data"]["curve"]
    i = 0
    while i < len(curve):
        speed.append(float(curve[i]["speed"]))
        coefficient.append(float(curve[i]["congestIndex"]))
        i += 12
    resultItem = {"name": roadNameList[roadIndex], "location": {"lon": lon, "lat": lat}, "speed": speed,
                  "coefficient": coefficient, "date": nowTime}
    coll_traffic.insert(resultItem)

# 路段实时拥堵系数
realtimeCoefficientUrl = "http://jiaotong.baidu.com/trafficindex/city/road?cityCode=131"
request = urllib2.Request(realtimeCoefficientUrl)
response = urllib2.urlopen(request)
realtimeCoefficient = json.loads(response.read())
highwayCoefficient = float(realtimeCoefficient["data"]["detail"]["highway_index"])
generalwayCoefficient = float(realtimeCoefficient["data"]["detail"]["general_way_index"])
highwayRate = float(realtimeCoefficient["data"]["detail"]["highway_week_rate"]) * 100
generalwayRate = float(realtimeCoefficient["data"]["detail"]["general_way_week_rate"]) * 100
highwaySpeed = float(realtimeCoefficient["data"]["detail"]["highway_speed"])
generalwaySpeed = float(realtimeCoefficient["data"]["detail"]["general_way_speed"])
resultItem = {"highway_coefficient": highwayCoefficient, "generalway_coefficient": generalwayCoefficient,
              "highway_rate": highwayRate, "generalway_rate": generalwayRate, "highway_speed": highwaySpeed,
              "generalway_speed": generalwaySpeed, "date": nowTime}
coll_traffic_coefficient.insert(resultItem)

# 路段实时拥堵里程
realtimeMileageUrl = "http://jiaotong.baidu.com/trafficindex/city/congestmile?cityCode=131"
request = urllib2.Request(realtimeMileageUrl)
response = urllib2.urlopen(request)
realtimeMileageJson = json.loads(response.read())
slowly = float(realtimeMileageJson["data"]["congest"]["slowly"])
congest = float(realtimeMileageJson["data"]["congest"]["congest"])
serious = float(realtimeMileageJson["data"]["congest"]["serious"])
avgSlowly = float(realtimeMileageJson["data"]["congest"]["avg_slowly"])
avgCongest = float(realtimeMileageJson["data"]["congest"]["avg_congest"])
avgSerious = float(realtimeMileageJson["data"]["congest"]["avg_serious"])
slowlyRate = float(realtimeMileageJson["data"]["congest"]["slowly_rate"]) * 100
congestRate = float(realtimeMileageJson["data"]["congest"]["congest_rate"]) * 100
seriousRate = float(realtimeMileageJson["data"]["congest"]["serious_rate"]) * 100
resultItem = {"slowly": slowly, "congest": congest, "serious": serious, "avg_slowly": avgSlowly,
              "avg_congest": avgCongest, "avg_serious": avgSerious, "slowly_rate": slowlyRate,
              "congest_rate": congestRate, "serious_rate": seriousRate, "date": nowTime}
coll_traffic_mileage.insert(resultItem)

# 早晚高峰
rushTimeUrl = "http://jiaotong.baidu.com/trafficindex/city/peakCongest?cityCode=131"
request = urllib2.Request(rushTimeUrl)
response = urllib2.urlopen(request)
rushTimeJson = json.loads(response.read())
morning_hour = rushTimeJson["data"]["peak_detail"]["morning_hour"]
morning_coefficient = float(rushTimeJson["data"]["peak_detail"]["morning_index"])
evening_hour = rushTimeJson["data"]["peak_detail"]["evening_hour"]
evening_coefficient = float(rushTimeJson["data"]["peak_detail"]["evening_index"])
resultItem = {"morning_hour": morning_hour, "morning_coefficient": morning_coefficient, "evening_hour": evening_hour,
              "evening_coefficient": evening_coefficient,"_id":datetime.datetime.now().strftime('%Y-%m-%d')}
coll_rushTime_mileage.save(resultItem)