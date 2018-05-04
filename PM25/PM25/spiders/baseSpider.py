# coding:utf-8

import scrapy
from scrapy import log
from PM25.items import rankPageItems
from PM25.getLatLon import getLatLon

class baseSpider(scrapy.Spider):

    name = "baseSpider"
    getLatLon = getLatLon()



    def parse(self, response):
        pass

    def parse_rankPage(self,response):
        # 页面一共两级 第一级是全国各个主要城市位置，点击各级之后会进入到二级页面，显示当地更为详细的站点的情况
        i = 1
        while i<368:
            # from scrapy.shell import inspect_response
            # inspect_response(response, self)
            rankItem = rankPageItems()
            rankItem["pageLevel"] = ["1"]
            rankItem["city"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[2]/a/text()").extract()
            rankItem["aqi"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[3]/text()").extract()
            rankItem["air_mark"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[4]/text()").extract()
            rankItem["pm25"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[6]/text()").extract()
            rankItem["pm_10"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[7]/text()").extract()
            rankItem["co"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[8]/text()").extract()
            rankItem["no2"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[9]/text()").extract()
            rankItem["o3"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[10]/text()").extract()
            rankItem["o3_8"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[11]/text()").extract()
            rankItem["so2"] = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[12]/text()").extract()
            contentPage = response.xpath("/html/body/div[2]/div/div[7]/table/tbody/tr[" + str(i) +"]/td[2]/a/@href").extract()
            if len(contentPage):
                # 生成二级页面url
                url = "http://www.pm25.in"+contentPage[0].encode("utf-8")
                # yield scrapy.Request(url, callback=self.parse_content)
            yield rankItem
            i += 1

    def parse_content(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        i = 1
        city = response.xpath("/html/body/div[2]/div[1]/div[1]/div[1]/h2/text()").extract()[0].encode("utf-8")
        point = {"city":city}
        self.getLatLon.process_city(point,log)
        while i:
            rankItem = rankPageItems()
            if point.has_key("cityId"):
                rankItem["cityId"]=[str(point["cityId"])]
            rankItem["pageLevel"] = ["2"]
            rankItem["city"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[1]/text()").extract()
            if len(rankItem["city"]):
                rankItem["city"][0] = city.decode("utf-8") + rankItem["city"][0]
                rankItem["aqi"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[2]/text()").extract()
                rankItem["air_mark"] = response.xpath('//*[@id="detail-data"]/tbody/tr[' + str(i) +"]/td[3]/text()").extract()
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
