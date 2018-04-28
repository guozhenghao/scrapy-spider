# encoding:utf-8
import time
import datetime

sendTime = u"8月14日 12:38"
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


print sendTime