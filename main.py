from datetime import date, datetime, timedelta
import math
import json
import requests
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now() + timedelta(hours=8)
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]

city="广州白云"


# 爬取爱词霸每日鸡汤
def get_iciba_everyday_chicken_soup():
  url = 'http://open.iciba.com/dsapi/'  # 词霸免费开放的jsonAPI接口
  r = requests.get(url)
  all = json.loads(r.text)  # 获取到json格式的内容，内容很多
  # print(all) # json内容，通过这行代码来确定每日一句的键名
  Englis = all['content']  # 提取json中的英文鸡汤
  Chinese = all['note']  # 提取json中的中文鸡汤
  everyday_soup = Englis + '\n' + Chinese  # 合并需要的字符串内容
  return everyday_soup  # 返回结果

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

def get_weather():
  tqurl="https://devapi.qweather.com/v7/weather/3d"
  recommendUrl = 'https://devapi.qweather.com/v7/indices/1d?type=3,13&location=101280110&key=a9633d3d76964a25aa7360aeae53a801'

  value = {
    'location': '101280110',
    'key': 'a9633d3d76964a25aa7360aeae53a801',#1fb7bd7b7a224138b85e1d2f570b86a1
    'lang': 'zh'


  }

  ybreq = requests.get(tqurl, params=value)
  cyreq = requests.get(recommendUrl)

  ybjs = ybreq.json()
  cyjs = cyreq.json()

  yb=ybjs["daily"]
  print(yb)
  return yb[0]["tempMax"],yb[0]["tempMin"],yb[0]["windDirDay"],yb[0]['textDay'],cyjs["daily"][0]["text"],cyjs["daily"][1]["text"]


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
highTem,minTem,windDir,curWeather,shushiRec,dressRec=get_weather()
recommend1=shushiRec+" "+dressRec
recommend="嘻嘻，迟来的问候，晚风瑟瑟，记得添衣保暖。"
print(highTem,  minTem,  windDir,   curWeather,  shushiRec,  dressRec)
everydaySoup=get_iciba_everyday_chicken_soup()
data = {
  "city":{"value":city,"color":get_random_color()},
  "date":{"value":today.strftime('%Y年%m月%d日'),"color":get_random_color()},
  "weather":{"value":curWeather,"color":get_random_color()},
  "windDir":{"value":windDir,"color":get_random_color()},
  "recommend":{"value":recommend,"color":get_random_color()},
  "everydaySoup":{"value":get_iciba_everyday_chicken_soup(),"color":get_random_color()},
  "love_days":{"value":get_count(),"color":get_random_color()},
  "birthday_left":{"value":get_birthday(),"color":get_random_color()},
  "words":{"value":get_words(),"color":get_random_color()},
  "highest": {"value":highTem,"color":get_random_color()},
  "lowest":{"value":minTem, "color":get_random_color()}}
count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")
