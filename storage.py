# coding:utf-8
"""Some operating about the leancloud sotrage"""
import leancloud
import os
from bs4 import BeautifulSoup
import requests

# Secret
ID = os.environ["LEANCLOUD_ID"] = "m8BCOVzOjD2oa4o5ueVoYq16-gzGzoHsz"
KEY = os.environ["LEANCLOUD_KEY"] = "WPxGStevqfwNmgqCSEliPNpz"

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

		self.douyu_url = 'http://www.douyu.com'
		self.xiongmao_url = 'http://www.panda.tv'
		self.quanmin_url = 'http://www.quanmin.tv'
		self.zhanqi_url = 'http://www.zhanqi.tv'
		self.huya_url = "http://www.huya.com"
		self.longzhu_url = "http://longzhu.com"
		self.cc_url = 'http://cc.163.com'

	def douyu(self):
		url = "https://www.douyu.com/directory/game/LOL"
		try:
			response = requests.get(url, headers=self.headers, verify=False)
			soup = BeautifulSoup(response.content, "lxml")
			rooms = soup.find("ul", id="live-list-contentbox").find_all("li")
		except Exception as e:
			print e

		for room in rooms:
			name = room.find("span", {"class":"dy-name ellipsis fl"}).string.strip()
			people = room.find("span", {"class":"dy-num fr"}).string.strip()
			title = room.find("h3", {"class":"ellipsis"}).text.strip()
			img = room.find("img")["data-original"]
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
			response = requests.get(url, headers=self.headers, verify=False)
			soup = BeautifulSoup(response.content, "lxml")
			rooms = soup.find("ul", id="sortdetail-container").find_all("li")
		except Exception as e:
			print e

		for room in rooms:
			name = room.find("span", {"class":"video-nickname"}).text.strip()
			people = room.find("span", {"class":"video-number"}).string.strip()
			title = room.find("span", {"class":"video-title"})["title"]
			img = room.find("img")["data-original"]
			link = room.find("a", {"class":"video-list-item-wrap"})["href"]

			people = people.replace(u"人", '')
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

	def quanmin(self):
		url = self.quanmin_url + "/game/lol/"
		rooms = []
		try:
			# Iterate the pages
			for i in range(1,3):
				params = {"p":i}
				response = requests.get(url, params=params, headers=self.headers, verify=False)
				soup = BeautifulSoup(response.content, "lxml")

				# Find the max page
				page_num = soup.find_all("a", {"class":"list_w-paging_btn list_w-paging_num "})[-1]
				# Rooms' tag
				room_list = soup.find("ul", {"class":"list_w-videos_video-list"}).find_all("li")
				rooms.extend(room_list)
		except Exception as e:
			print e

		for room in rooms:
			name = room.find("span", {"class":"common_w-card_host-name"}).string
			people = room.find("span", {"class":"common_w-card_views-num"}).string
			title = room.find("p", {"class":"common_w-card_title"}).string
			img = room.find("img", {"class":"common_w-card_cover"})["src"]
			link = room.find("a", {"class":"common_w-card_href"})["href"]

			live = self.Live()
			live.type = "quanmin"

			live.set("type", "quanmin")
			live.set("name", name)
			live.set("people", int(people))
			live.set("link", "http:"+link)
			live.set("title", title)
			live.set("img", img)
			self.lives.append(live)

	def zhanqi(self):
		pass

	def huya(self):
		pass

	def longzhu(self):
		pass

	def cc(self):
		pass

	def fetch_all(self):
		"""Fetch all Live rooms"""
		self.douyu()
		self.xiongmao()
		self.quanmin()
		self.zhanqi()
		self.huya()
		self.longzhu()
		self.cc()

class Query(object):
	"""Some method for query"""
	@property
	def datas(self):
		query = leancloud.Query('Live')
		allDataCompleted = False
		batch = 0
		limit = 1000
		resultList = []  # All data
		while not allDataCompleted:
			# Set the limit showed data
			query.limit(limit)
			query.add_ascending('people')
			resultList.extend(query.find())
			if len(resultList) < limit:
				allDataCompleted = True
		return resultList
		
	def cleanData(self):
		"""Clean all data from cloud"""
		# Delete data
		leancloud.Object.destroy_all(self.datas)
