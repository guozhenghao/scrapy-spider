# coding:utf-8
import scrapy
from zipCodeSpider.items import ZipcodespiderItem
import time
import codecs
import traceback
import os
# linux时用
# import sys 
# reload(sys) 
# sys.setdefaultencoding('utf-8')


class zipCodeSpider(scrapy.Spider):
    
    name = "zipCodeSpider"

    allowed_domains = ["yb21.cn"]
    def __init__(self):
        # collid用于数据库中id值
        self.collid = 100000
        filepath = os.getcwd()
        self.fi = open(filepath+r'\zipCodeSpider\result\result1.txt','w')
        self.fi2 = open(filepath+r'\zipCodeSpider\result\result2.txt','w')
        # self.fi3 = codecs.open(filepath+r'\zipCodeSpider\result\result3.txt','w','utf-8')
        super(zipCodeSpider,self).__init__()

    def start_requests(self):

        try:
            # 爬取第一个页面，得到所有省市链接      
            url = "http://www.yb21.cn/post/"
            yield scrapy.Request(url,callback=self.parse_basePage)
        except BaseException, e:
            self.logger.error("ERROR: start " + repr(e))
            self.close(self.name, repr(e))

    def parse_basePage(self,response):

        # 爬取第一个页面的省市链接，拼接到url，用于进入第二页面获得该省市下的所有邮编
        province = 1
        city = 1
        try:
            while province < 32:
                city = 1
                while city < 30:
                    link = response.xpath("/html/body/table[2]/tbody[1]/tr[2]/td/div["+str(province)+"]/ul/a["+ str(city)+"]/@href").extract()
                    if len(link) is 0:
                        break
                    url = "http://www.yb21.cn" + link[0]
                    city += 1
                    self.fi.write(url + "\n")
                    yield scrapy.Request(url,callback=self.parse_secondPage)
                province += 1
        except BaseException, e:
            self.logger.error("ERROR: base " + repr(e))
            self.close(self.name, repr(e))
    def parse_secondPage(self,response):

        # 爬取页面中的所有邮编信息，将邮编进行拼接，用于进入第三个页面，爬取第三页面中该邮编下的所属地址    
        tr = 2
        td = 1
        try:
            while tr < 27:
                td = 1
                while td < 7:
                    link = response.xpath("/html/body/table[3]/tbody/tr[" + str(tr) + "]/td[" + str(td) +"]/strong/a/@href").extract()
                    if len(link) is 0:
                        break               
                    url = "http://www.yb21.cn" + link[0]
                    td += 1
                    self.fi2.write(url + "\n")
                    yield scrapy.Request(url,callback=self.parse_finalPage)
                tr += 1
        except BaseException, e:
            self.logger.error("ERROR: " + repr(e))
            self.close(self.name, repr(e))

    def parse_finalPage(self,response):

        # 通过爬取第三页面，将该邮编下的各个所属地址，与该邮编添加到数据库
        finalItem = ZipcodespiderItem()        
        tr = 2
        td = 1
        # 串的开始是u'xd3' a的值是每个页面最后的无用值开始
        # a = u'xd3\xca\xd5'
        try:            
            tempFinalCode = response.xpath("/html/body/table[2]/tbody/tr[1]/td/h1/text()").extract()
            finalItem["zipCode"] = tempFinalCode[0].encode('utf-8')
            # 串的开始是u'xd3' a的值是每个页面最后的无用值开始
            # a = u'xd3\xca\xd5'            
            while tr < 50:
                td = 1
                while td < 4:
                    # 用于字符集转换，解决乱码问题
                    tempFinalPlace = response.xpath("/html/body/table[2]/tbody/tr[3]/td/table/tbody/tr[" + str(tr) + "]/td[" + str(td) + "]/text()").extract()
                    if len(tempFinalPlace) is 0:
                        break
                    # 已封装成方法（transition）
                    # tempFinalPlace = codecs.unicode_escape_encode(tempFinalPlace[0][1:])
                    # tempFinalPlace = codecs.escape_decode(tempFinalPlace[0]) 
                    tempFinalPlace = self.transition(tempFinalPlace)
                    # 每一页面最后都有一个无用项会报错
                    if tempFinalPlace.startswith('\xca\xd5\xfe'):
                        break
                    # 有的邮编下显示该地方的所有街道，进行处理
                    
                    # Windows下用的if
                    if u"所有街道" in tempFinalPlace:
                    # linux下“所有街道”前不用加u（后面的邮政和邮政编码在linux下写utf-8，windows下用gbk）
                    # if "所有街道" in tempFinalPlace:
                        tempFinalPlace = response.xpath('/html/body/table[2]/tbody/tr[2]/td[2]/a[2]/text()').extract()
                        tempFinalPlace = self.transition2(tempFinalPlace)
                    # 有的邮编下显示为地址+邮编或邮编编码，进行格式化

                    # Windows下用
                    tempFinalPlace = tempFinalPlace.replace("邮编".encode("gbk"),"")
                    tempFinalPlace = tempFinalPlace.replace("邮政编码".encode("gbk"),"")
                    # linux用
                    # tempFinalPlace = tempFinalPlace.replace("邮编".encode("utf-8"),"")
                    # tempFinalPlace = tempFinalPlace.replace("邮政编码".encode("utf-8"),"")
                    
                    finalItem["place"] = tempFinalPlace.decode('gbk').encode('utf-8')                   
                    self.collid = self.collid+1
                    finalItem["_id"] = self.collid
                    td += 1
                    yield finalItem                
                tr += 1
        except BaseException, e:
            self.logger.error("ERROR: final " + repr(e))
            self.logger.error("ERROR: treeback: "+ str(traceback.print_exc()))
            self.close(self.name, repr(e))     

    # 下面两个方法相同，只是开始位不一样，返回值加上了【0】，直接返回字符串，使用时就不用再...【0】了      
    # 该方法从第2位开始，是因为数据前有一个&nbsp;
    def transition(self,item):
        item = codecs.unicode_escape_encode(item[0][1:])
        item = codecs.escape_decode(item[0]) 
        return item[0]
    # 方法同上，开头没有特殊符号，从第一位开始
    def transition2(self,item):
        item = codecs.unicode_escape_encode(item[0])
        item = codecs.escape_decode(item[0]) 
        return item[0]