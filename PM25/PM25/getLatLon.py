# coding:utf-8
import urllib2
import json
import traceback
from pymongo import MongoClient
from urllib import quote_plus


class getLatLon(object):

    def transAmap(self, city, log):
        cityInfoAmap = {}
        try:
            url = (u'http://restapi.amap.com/v3/geocode/geo?key=自己的key值&s=rsv3&address=' + city.decode(
            "utf-8")).encode("utf-8").replace(u"地区".encode("utf-8"),"")
            request = urllib2.Request(url)
            body = urllib2.urlopen(request).read()
            cityInfoAmap = json.loads(body)
            cityInfoAmap = cityInfoAmap["geocodes"][0]
            cityInfo = {}
            cityInfo["province"] = cityInfoAmap["province"]
            cityInfo["city"] = cityInfoAmap["city"]
            cityInfo["district"] = cityInfoAmap["district"]
            location = cityInfoAmap["location"].split(",")
            cityInfo["lon"] = float(location[0])
            cityInfo["lat"] = float(location[1])
            return cityInfo
        except BaseException, e:
            log.msg("transAmap: " + repr(e), log.WARNING)