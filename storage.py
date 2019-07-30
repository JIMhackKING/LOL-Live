# coding:utf-8
"""Some operating about the leancloud sotrage"""
import leancloud
import os
from bs4 import BeautifulSoup
import requests

# Secret
ID = os.environ["LEANCLOUD_ID"]
KEY = os.environ["LEANCLOUD_KEY"]

# Init the leancloud
leancloud.init(ID, KEY)

class Fetch(object):
	"""Fetch all from all the Live platform"""
	Live = leancloud.Object.extend("Live")

	def __init__(self):
		self.lives = []
		self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) "
						"AppleWebKit/537.36 (KHTML, like Gecko) "
						"Chrome/59.0.3071.115 Safari/537.36"}
		self.maximum = 20

		self.douyu_url = 'http://www.douyu.com'
		self.xiongmao_url = 'http://www.panda.tv'
		self.quanmin_url = 'http://www.quanmin.tv'
		self.zhanqi_url = 'http://www.zhanqi.tv'
		self.huya_url = "http://www.huya.com"
		self.longzhu_url = "http://longzhu.com"

	def douyu(self):
		url = "https://www.douyu.com/g_LOL"
		try:
			response = requests.get(url, headers=self.headers)
			soup = BeautifulSoup(response.content, "lxml")
			section_all = soup.find("section", id="listAll")
			rooms = section_all.find("ul", {"class": "layout-Cover-list"}).find_all("li", {"class": "layout-Cover-item"})
		except Exception as e:
			print e

		for index, room in enumerate(rooms):
			if index == self.maximum:
				break
			name = room.find("span", {"h2":"DyListCover-user"}).string.strip()
			people = room.find("span", {"class":"DyListCover-hot"}).string.strip()
			title = room.find("h3", {"class":"DyListCover-intro"}).text.strip()
			img = room.find("img")["src"]
			link = room.find("a")["href"]

			# trans people to num
			if u"万" in people:
				people = int(float(people.replace(u"万", "")) * 10000)

			live = self.Live()
			live.type = "douyu"
			live.set("type", live.type)
			live.set("name", name)
			live.set("people", int(people))
			live.set("title", title)
			live.set("img", img)
			live.set("link", self.douyu_url+link)
			self.lives.append(live)

	def xiongmao(self):
		url = "https://www.panda.tv/cate/lol"
		try:
			response = requests.get(url, headers=self.headers)
			soup = BeautifulSoup(response.content, "lxml")
			rooms = soup.find("ul", id="sortdetail-container").find_all("li")
		except Exception as e:
			print e

		for index, room in enumerate(rooms):
			if index == self.maximum:
				break
			name = room.find("span", {"class":"video-nickname"}).text.strip()
			people = room.find("span", {"class":"video-number"}).string.strip()
			title = room.find("span", {"class":"video-title"})["title"]
			img = room.find("img")["data-original"]
			link = room.find("a", {"class":"video-list-item-wrap"})["href"]

			people = people.replace(u"人", '')
			if u"万" in people:
				people = int(float(people.replace(u"万", "")) * 10000) 

			live = self.Live()
			live.type = "xiongmao"
			live.set("type", live.type)
			live.set("name", name)
			live.set("people", int(people))
			live.set("title", title)
			live.set("img", img)
			live.set("link", self.douyu_url+link)
			self.lives.append(live)

	def quanmin(self):
		url = "http://m.quanmin.tv/json/categories/lol/list.json?_t=201708231430"
		try:
			response = requests.get(url, headers=self.headers).json()
			rooms = response["data"]
		except Exception as e:
			print e

		for index, room in enumerate(rooms):
			if index == self.maximum:
				break
			name = room["nick"]
			people = room["view"]
			title = room["title"]
			img = room["thumb"]
			link = room["no"]

			live = self.Live()
			live.type = "quanmin"

			live.set("type", "quanmin")
			live.set("name", name)
			live.set("people", int(people))
			live.set("link", self.quanmin_url+"/"+link)
			live.set("title", title)
			live.set("img", img)
			self.lives.append(live)

	def zhanqi(self):
		for i in (1,):
			url = "http://www.zhanqi.tv/api/static/v2.1/game/live/6/30/%d.json" %i
			response = requests.get(url, headers=self.headers).json()
			rooms = response["data"]["rooms"]

			for room in rooms:
				name = room["nickname"]
				people = room["online"]
				title = room["title"]
				img = room["bpic"]
				link = self.zhanqi_url + room["url"]

				live = self.Live()
				live.type = "zhanqi"

				live.set("type", live.type)
				live.set("name", name)
				live.set("people", int(people))
				live.set("link", link)
				live.set("title", title)
				live.set("img", img)
				self.lives.append(live)

	def huya(self):
		url = "http://www.huya.com/g/lol"
		try:
			response = requests.get(url, headers = self.headers)
			soup = BeautifulSoup(response.content, 'lxml')
			rooms = soup.find("ul", id="js-live-list").find_all("li")
		except Exception as e:
			print e

		for index, room in enumerate(rooms):
			if index == self.maximum:
				break
			name = room.find("i", {"class":"nick"}).string.strip()
			people = room.find("i", {"class":"js-num"}).string.strip()
			title = room.find("a", {"class":"title"}).string.strip()
			img = room.find("img", {"class":"pic"})["data-original"]
			link = room.find("a")["href"]

			if u"万" in people:
				people = int(float(people.replace(u"万", "")) * 10000)

			live = self.Live()
			live.type = "huya"

			live.set("type", live.type)
			live.set("name", name)
			live.set("people", int(people))
			live.set("link", link)
			live.set("title", title)
			live.set("img", img)
			self.lives.append(live)

	def longzhu(self):
		url = "http://api.plu.cn/tga/streams"
		rooms = []
		for i in (0,):
			params = {"max-results": "18",
					"start-index": i * 18,
					"sort-by": "top",
					"filter": "0", "game": "4"}

			response = requests.get(url, params=params, headers=self.headers).json()
			items = response["data"]["items"]
			if not items:
				break
			else:
				rooms.extend(items)

		for room in rooms:
			name = room["channel"]["name"]
			people = room["viewers"]
			title = room["channel"]["status"]
			img = room["preview2"]
			link = room["channel"]["url"]

			live = self.Live()
			live.type = "longzhu"

			live.set("type", live.type)
			live.set("name", name)
			live.set("people", int(people))
			live.set("link", link)
			live.set("title", title)
			live.set("img", img)
			self.lives.append(live)

	def fetch_all(self):
		"""Fetch all Live rooms"""
		try:
			self.douyu()
		except:
			pass
		try:
			self.xiongmao()
		except:
			pass
		try:
			self.quanmin()
		except:
			pass
		try:
			self.zhanqi()
		except:
			pass
		try:
			self.huya()
		except:
			pass
		try:
			self.longzhu()
		except:
			pass

class Query(object):
	"""Some method for query"""

	@property
	def datas(self):
		query = leancloud.Query('Live')
		allDataCompleted = False
		batch = 0
		limit = 1000

		# get all data
		resultList = []  # All data
		while not allDataCompleted:
			# Set the limit showed data
			query.limit(limit)
			# reverse arrangement
			query.add_descending('people')
			resultList.extend(query.find())
			if len(resultList) < limit:
				allDataCompleted = True
		return resultList
		
	def cleanData(self):
		"""Clean all data from cloud"""
		# Delete data
		leancloud.Object.destroy_all(self.datas)

if __name__ == '__main__':
	query = Query()
	datas = query.datas[0:60]
	print datas
