# -*- coding: utf-8 -*-
import scrapy
import os
import re
from selenium import webdriver
import traceback
from time import sleep
from selenium.webdriver.common.keys import Keys
import urllib2
from lxml import etree
import json
import codecs
import datetime
import time
from pymongo import MongoClient

# 总体说一下，if page == 1 else 是因为第一页和别的也结构不一样，因为没有时间，后期会将处理写成一个方法然后传入参数，这样可以减少重复代码量

class weiboSpider(scrapy.Spider):
    
    name = "weiboSpider"

    def __init__(self):
        # 自己的地址和端口号
        dbClient  = MongoClient("111.111.111.111",11111)
        dbname = "national_regionalism"
        db = dbClient[dbname]
        self.coll_weiboHighTemperature = db["weibo_highTemperature"]

        filepath = os.getcwd()
        self.fi = open(r'D:\VSCode\workspace\weiboKeyWordSearchSpider\result\result1.txt','w')
        self.fi2 = open(r'D:\VSCode\workspace\weiboKeyWordSearchSpider\result\result2.txt','w')
        super(weiboSpider,self).__init__()

    def start_requests(self):
        
        try:
            # 因为使用phantomjs登陆非常麻烦，所有直接使用selenium进行有界面的环境进行爬取，一下步骤为在用户名和密码进行填写然后点击登录
            browser = webdriver.Chrome()
            browser.get('http://weibo.com/')
            sleep(5)
            browser.find_element_by_id('loginname').clear()
            # 自己的用户名和密码
            browser.find_element_by_id('loginname').send_keys("111111111111111")
            browser.find_element_by_name('password').clear()
            browser.find_element_by_name('password').send_keys("1111111111111")
            sleep(5)
            browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').send_keys(Keys.ENTER)
            sleep(5)
            # sreach_window=browser.current_window_handle
            # browser.maximize_window()
            
            pattern = re.compile('\U.*?')
            for page in range(22,50):
                # 以搜索关键词 高温 为例
                browser.get('http://s.weibo.com/weibo/高温&page='+str(page))
                self.fi.write(str(page)+'\n')
                print page
                if page == 10:
                    break
                if page == 1:
                    
                    for item in range(1,19):
                        # text为正文信息，因为与展开选文选项，需要特别处理，分析网站结合代码即可懂
                        try:
                            textLink = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p/a[1]')  
                        except:
                            textLink = 0
                        if textLink == 0:
                            text = browser.find_elements_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                            text = text[0].text.replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")                            
                        else:
                            for j in range(2,10):
                                try:
                                    textLink = textLink.get_attribute("action-data")
                                    if textLink is None:
                                        textLink = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p/a[' + str(j) +']')
                                    else:
                                        break
                                except:
                                    pass
                            if textLink is None:
                                text = browser.find_elements_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                                text = text[0].text.replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                            else:
                                textLink = "http://s.weibo.com/ajax/direct/morethan140?"+textLink
                                try:
                                    resultTemp = urllib2.urlopen(textLink)
                                    jsonInfo = resultTemp.read()
                                    jsonFile = json.loads(jsonInfo)
                                    text = jsonFile['data']['html'].replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                                except:
                                    text = browser.find_elements_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                                    text = text[0].text.replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                        text = codecs.escape_decode(codecs.unicode_escape_encode(text)[0])[0]
                        pattern = re.compile(r'\\U.{8}',re.U)
                        text = re.sub(pattern,'',str(text))
                        text = codecs.unicode_escape_decode(text)[0]     
                        userName = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/a[1]')
                        userName = userName.text
                        userHead = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[2]/a/img')
                        userHead = userHead.get_attribute("src")
                        sendTime = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[2]/a[1]')
                        sendTime = sendTime.text
                        dt = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "%Y-%m-%d %H:%M:%S")
                        # 格式化时间信息，因为有xx秒前、xx分钟前、今天xxx等
                        if u"秒" in sendTime:
                            sendTime = dt + datetime.timedelta(seconds= -int(sendTime.split(u"秒")[0]))
                            sendTime = sendTime.strftime("%Y-%m-%d %H:%M:%S")
                        elif u"分钟" in sendTime:
                            sendTime = dt + datetime.timedelta(minutes= -int(sendTime.split(u"分钟")[0]))
                            sendTime = sendTime.strftime("%Y-%m-%d %H:%M:%S")
                        elif u"今天" in sendTime:
                            sendTime = time.strftime('%Y-%m-%d', time.localtime(time.time())) + sendTime.split(u"今天")[1] + ":00"
                        else:
                            sendTime = time.strftime('%Y', time.localtime(time.time())) + "-"+sendTime.split(u"月")[0]+"-"+sendTime.split(u"月")[1].split(u"日")[0]+ sendTime.split(u"日")[1]+":00"
                        # sendFrom是使用什么发出的微博，有的选项为空，做特殊处理
                        try:
                            sendFrom = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[2]/a[2]')
                            sendFrom = sendFrom.text
                        except:
                            sendFrom = u"无"
                        shareCount = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[2]/ul/li[2]/a/span/em')
                        shareCount = shareCount.text
                        if len(shareCount) == 0:
                            shareCount = "0"
                        try:
                            commondCount = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[2]/ul/li[3]/a/span/em')
                            commondCount = commondCount.text
                        except:
                            commondCount = "0"
                        goodCount = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[3]/div/div[' + str(item) + ']/div/div[2]/ul/li[4]/a/span/em')
                        goodCount = goodCount.text
                        if len(goodCount) == 0:
                            goodCount = "0"
                        try:
                            self.coll_weiboHighTemperature.insert({"userName":userName,"userHead":userHead,"text":text,"sendTime":sendTime,"sendFrom":sendFrom,"shareCount":shareCount,"commondCount":commondCount,"goodCount":goodCount})
                            self.fi2.write(userName+'\n'+userHead+'\n'+ text+'\n'+ sendTime+'\n'+sendFrom+'\n'+shareCount+'\n'+commondCount+'\n'+goodCount+'\n')
                            print "**************************"+str(item)
                        except:
                            # 特殊字符多为手机自带的特殊字符，这个编码问题懒得处理了，pass
                            self.fi2.write("有个傻叉又搞特殊字符"+"\n")
                    sleep(5)    
                else:
                    for item in range(2,20):
                        try:
                            textLink = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p/a[1]')  
                        except:
                            textLink = 0
                        if textLink == 0:
                            text = browser.find_elements_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                            text = text[0].text.replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                        else:
                            # textLink = textLink[0].get_attribute('action-date')
                            for j in range(2,10):
                                try:
                                    textLink = textLink.get_attribute("action-data")
                                    if textLink is None:
                                        textLink = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p/a[' + str(j) +']')
                                    else:
                                        break
                                except:
                                    pass
                            if textLink is None:
                                text = browser.find_elements_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                                text = text[0].text.replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                            else:
                                textLink = "http://s.weibo.com/ajax/direct/morethan140?"+textLink
                                try:
                                    resultTemp = urllib2.urlopen(textLink)
                                    jsonInfo = resultTemp.read()
                                    jsonFile = json.loads(jsonInfo)
                                    text = jsonFile['data']['html'].replace(u'#','').replace(u' ','').replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                                except:
                                    text = browser.find_elements_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                                    text = text[0].text.replace(u"#","").replace(u" ","").replace(u'&#8203;',"").replace(u'&#nbsp;',"")
                        text = codecs.escape_decode(codecs.unicode_escape_encode(text)[0])[0]
                        pattern = re.compile(r'\\U.{8}',re.U)
                        text = re.sub(pattern,'',str(text))
                        text = codecs.unicode_escape_decode(text)[0]
                        userName = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[1]/a[1]')
                        userName = userName.text
                        userHead = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[2]/a/img')
                        userHead = userHead.get_attribute("src")    
                        sendTime = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[2]/a[1]')
                        sendTime = sendTime.text
                        dt = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "%Y-%m-%d %H:%M:%S")
                        if u"秒" in sendTime:
                            sendTime = dt + datetime.timedelta(seconds= -int(sendTime.split(u"秒")[0]))
                            sendTime = sendTime.strftime("%Y-%m-%d %H:%M:%S")
                        elif u"分钟" in sendTime:
                            sendTime = dt + datetime.timedelta(minutes= -int(sendTime.split(u"分钟")[0]))
                            sendTime = sendTime.strftime("%Y-%m-%d %H:%M:%S")
                        elif u"今天" in sendTime:
                            sendTime = time.strftime('%Y-%m-%d', time.localtime(time.time())) + sendTime.split(u"今天")[1] + ":00"
                        else:
                            sendTime = time.strftime('%Y', time.localtime(time.time())) + "-"+sendTime.split(u"月")[0]+"-"+sendTime.split(u"月")[1].split(u"日")[0]+ sendTime.split(u"日")[1]+":00"
                        try:
                            sendFrom = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[1]/dl/div/div[3]/div[2]/a[2]')
                            sendFrom = sendFrom.text
                        except:
                            sendFrom = u"无"
                        shareCount = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[2]/ul/li[2]/a/span/em')
                        shareCount = shareCount.text
                        if len(shareCount) == 0:
                            shareCount = "0"
                        try:
                            commondCount = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[2]/ul/li[3]/a/span/em')
                            commondCount = commondCount.text
                        except:
                            commondCount = "0"
                        goodCount = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div/div[' + str(item) + ']/div/div[2]/ul/li[4]/a/span/em')
                        goodCount = goodCount.text
                        if len(goodCount) == 0:
                            goodCount = "0"
                        try:
                            self.coll_weiboHighTemperature.insert({"userName":userName,"userHead":userHead,"text":text,"sendTime":sendTime,"sendFrom":sendFrom,"shareCount":shareCount,"commondCount":commondCount,"goodCount":goodCount})  
                            self.fi2.write(userName+'\n'+userHead+'\n'+ text+'\n'+ sendTime+'\n'+sendFrom+'\n'+shareCount+'\n'+commondCount+'\n'+goodCount+'\n')
                            print "***********************************"+str(item)
                        except:
                            self.fi2.write(u"有个傻叉又搞特殊字符")
                    sleep(5)

            
        except BaseException, e:
            self.logger.error("ERROR : start  " + repr(e))
            self.close(self.name, repr(e))