# coding:utf-8
import urllib2
import json
import traceback
from pymongo import MongoClient
from urllib import quote_plus


class getLatLon(object):

    def __init__(self):
        """
        初始化数据库连接，缓存城市地址表
        """
        uri = "mongodb://%s:%s@%s" % (quote_plus('root'), quote_plus('密码'), 'ip:port')
        dbClient  = MongoClient(uri)
        dbname = "national_regionalism"
        self.db = dbClient[dbname]

        # transAmap 使用
        # self.coll_point = self.db["pointInfo"]

        # process_city
        coll_city = self.db["new_city"]
        citysInfo = coll_city.find({},{"_id":0,"coordinates":0,"border":0,"location":0})
        self.citys = []
        try:
            while True:
                self.citys.append(citysInfo.next())
        except :
            pass
        # process_point
        coll_point = self.db["pointInfo"]
        pointsInfo = coll_point.find()
        self.points = []
        try:
            while True:
                self.points.append(pointsInfo.next())
        except :
            pass

    def process_city(self,item, log):
        """
        转化城市的坐标（仅限cityInfo表）
        parms:
            item :
                字典型，有以下字段要求
                    至少包含"city"字段:表示需要从cityInfo表里获取_id的城市名称
                    不能包含"cityId"字段:cityId用来存储提取到的_id值
                举例: scrapy 的 item . {"city":"北京市","aqi":24}
            log ： 日志记录类
        return:None
            如果cityInfo表里name/alias项有此城市，则会将其_id加到item中. 否则记录异常
        """
        try:
            hasalias = False
            city_item = item["city"].decode("utf-8")
            for city in self.citys:
                if city_item in city["name"]:
                    item["cityId"] = city["code"]
                    hasalias = True
                    break
                if city.has_key("alias"):
                    for alia in city["alias"]:
                        if city_item in alia:
                            item["cityId"] = city["code"]
                            hasalias = True
                            break
                    if hasalias:
                        break
            if not hasalias:
                log.msg("No City: "+ city_item +" in Mongo", log.WARNING)
                pass
        except BaseException,e:
            log.msg("process_City: "+ item["city"].decode("utf-8") +repr(e), log.WARNING)
            # log.msg("process_City: "+ item["city"] +repr(e), log.WARNING)

    def process_point(self, item, log):
        try:
            hasalias = False
            city_item = item["city"].decode("utf-8")
            for point in self.points:
                if city_item in point["point"]:
                    item["pointId"] = point["_id"]
                    hasalias = True
                    break
                if point.has_key("alias"):
                    for alia in point["alias"]:
                        if city_item in alia:
                            item["pointId"] = point["_id"]
                            hasalias = True
                            break
                    if hasalias:
                        break
            if not hasalias:
                log.msg("No Point: "+city_item+" in Mongo", log.WARNING)
                pass
        except BaseException,e :
            log.msg("process_point: "+ item["city"].decode("utf-8") + repr(e), log.WARNING)
            # log.msg("process_point: "+ item["city"] + repr(e), log.WARNING)

    def transAmap(self,point,log):
        """
        根据高德API转换坐标. 每个key每天限制调用次数: 20000
        parms:
            point:监测点地理位置: 城市+监测点. 如: "北京市金泉时代"
        """
        cityInfoAmap = {}
        try:
            url = (u'http://restapi.amap.com/v3/geocode/geo?key=自己的key&s=rsv3&address=' + point.decode("utf-8")).encode("utf-8")
            request = urllib2.Request(url)
            body = urllib2.urlopen(request).read()
            # log.msg("transAmap : "+str(body.decode("utf-8")), log.WARNING)
            cityInfoAmap = json.loads(body)
            cityInfoAmap = cityInfoAmap["geocodes"][0]
            cityInfo = {}
            cityInfo["province"] = cityInfoAmap["province"]
            cityInfo["city"] = cityInfoAmap["city"]
            cityInfo["district"] = cityInfoAmap["district"]
            cityInfo["point"] = cityInfoAmap["formatted_address"]
            cityInfo["alias"] = [point]
            location = cityInfoAmap["location"].split(",")
            cityInfo["lon"] = location[0]
            cityInfo["lat"] = location[1]
            self.coll_point.insert(cityInfo)
        except BaseException,e :
            log.msg("transAmap: " + repr(e), log.WARNING)
