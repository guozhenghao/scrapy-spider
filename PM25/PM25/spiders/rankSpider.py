# coding:utf-8

import scrapy
import traceback
from scrapy.exceptions import CloseSpider
from baseSpider import baseSpider

class rankSpider(baseSpider):


    name = "rankSpider"
    allowed_domains = ["pm25.in"]

    # 该方法必须返回一个可迭代的对象
    def start_requests(self):
        self.logger.warning("SCRAPY: Begin Crawl")
        try:
            url = 'http://www.pm25.in/rank'
            yield scrapy.Request(url, callback=self.parse)
        except BaseException, e:
            # 记录日志
            self.logger.error("ERROR")
            self.close(self.name, repr(e))
        else:
            #日志记录
            self.logger.warning("SCRAPY: crawl over correctly")

            self.close(self.name, "crawl over")
    
    def parse(self, response):
        try:
            return self.parse_rankPage(response)
        except BaseException, e:
            raise CloseSpider("IP have been forbidden")
