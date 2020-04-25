#!/usr/bin/env python
# -*-coding:UTF-8-*-
from bs4 import BeautifulSoup
import requests
import sys
import codecs
import os 
url = sys.argv[1]

curDir =  os.path.dirname(os.path.realpath(__file__))
curDir = os.path.join(curDir,"capture_log")

if len(sys.argv) > 2 :
	print(len(sys.argv))
	curDir = sys.argv[2]
	
if os.path.exists(curDir) != True:
	os.makedirs(curDir)

firstSeperatorIndex = url.find('/', url.find('//') + len('//'))
if firstSeperatorIndex < 0:
	rootUrl = url + '/'
else:
	rootUrl = url

wb_data = requests.get(url)

soup = BeautifulSoup(wb_data.text)

# print(soup)
logs = soup.findAll("a")

for x in logs:
	# help(x)
	href = x.get('href')
	if href.endswith(".log") or href.endswith(".txt") or href.endswith(".md") or href.endswith(".csv"):
		fileUrl = rootUrl + href
		try:
			print("%s downloading ..."%fileUrl)
			wd = requests.get(fileUrl)
			# out = open(x,"w")
			out = codecs.open(os.path.join(curDir,x.get_text()), "w", wd.encoding)
			print(os.path.join(curDir,x.get_text()))
			out.write(wd.text)
			out.close()
		except Exception as e:
			print(e)