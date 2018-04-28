# coding:utf-8

import scrapy
import time
import random
from scrapy import log
from PM25.items import rankPageItems
from pymongo import MongoClient
from PM25.getLatLon import getLatLon

class baseSpider(scrapy.Spider):

    name = "baseSpider"
    getLatLon = getLatLon()

    def parse(self, response):
        pass

    def parse_rankPage(self,response):
        ''' 保证所有的item字段格式都是 item['key'] = ['value'] ,因为后续处理都是默认item为这种格式 '''
        i = 1
        # time = response.xpath("/html/body/div[2]/div/div[6]/p/text()").extract()
        while i<368:
            rankItem = rankPageItems()
            # rankItem["updateDate"] = time
            rankItem["pageLevel"] = ["1"]
            rankItem["rank"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[1]/text()").extract()
            rankItem["city"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[2]/a/text()").extract()
            rankItem["aqi"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[3]/text()").extract()
            rankItem["air_mark"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[4]/text()").extract()
            rankItem["primary_Pollutant"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[5]/text()").extract()
            rankItem["pm25"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[6]/text()").extract()
            rankItem["pm_10"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[7]/text()").extract()
            rankItem["co"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[8]/text()").extract()
            rankItem["no2"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[9]/text()").extract()
            rankItem["o3"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[10]/text()").extract()
            rankItem["o3_8"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[11]/text()").extract()
            rankItem["so2"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[12]/text()").extract()
            contentPage = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[2]/a/@href").extract()
            if len(contentPage):
                url = "http://www.pm25.in"+contentPage[0].encode("utf-8")
                # yield scrapy.Request(url, callback=lambda response, rank = rankItem["rank"]: self.parse_content(response,rank))
                yield scrapy.Request(url, callback=self.parse_content)
            yield rankItem
            # log.msg(rankItem["rank"][0], log.WARNING)
            i += 1

    # def parse_content(self, response, rank):
    def parse_content(self, response):
        '''
            解析二级页面
        '''
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        i = 1
        # time = response.xpath("/html/body/div[2]/div[1]/div[2]/div[1]/p/text()").extract()
        city = response.xpath("/html/body/div[2]/div[1]/div[1]/div[1]/h2/text()").extract()[0].encode("utf-8")
        point = {"city":city}
        # log.msg("TEST:"+point["city"].encode("utf-8").decode("utf-8"),log.ERROR)
        self.getLatLon.process_city(point,log)
        while i:
            rankItem = rankPageItems()
            if point.has_key("cityId"):
                rankItem["cityId"]=[str(point["cityId"])]
            rankItem["pageLevel"] = ["2"]
            # rankItem["updateDate"] = time
            # rankItem["rank"] = rank
            rankItem["city"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[1]/text()").extract()
            if len(rankItem["city"]):
                rankItem["city"][0] = city.decode("utf-8") + rankItem["city"][0]
                rankItem["aqi"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[2]/text()").extract()
                rankItem["air_mark"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[3]/text()").extract()
                rankItem["primary_Pollutant"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[4]/text()").extract()
                rankItem["pm25"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[5]/text()").extract()
                rankItem["pm_10"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[6]/text()").extract()
                rankItem["co"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[7]/text()").extract()
                rankItem["no2"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[8]/text()").extract()
                rankItem["o3"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[9]/text()").extract()
                rankItem["o3_8"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[10]/text()").extract()
                rankItem["so2"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[11]/text()").extract()
                i += 1
                yield rankItem
            else:
                i = 0
