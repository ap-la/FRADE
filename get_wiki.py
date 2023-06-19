import urllib2
import sys
from bs4 import BeautifulSoup



add_links=[]


def process(x):
	result=[]
	link="http://localhost:8080/mediawiki/index.php/"
	url=link+x
	add_links.append(x)
	try:
		conn=urllib2.urlopen(url)
	except urllib2.HTTPError:
		return
	html=conn.read()
	soup=BeautifulSoup(html)
	new_links=soup.find_all('a')
	for link in new_links:
		x=link.get('href')
		if x is not None:
			if "/mediawiki/index.php/" in x and x.startswith("/mediawiki/") and "Category:" not in x and "Special:" not in x and "Main_Page" not in x and "Wikipedia:" not in x and "File:" not in x and "Help:" not in x:
				if x not in add_links:
					add_links.append(x) 

def dump_urls():
	dump=open("dump2.txt","w")
	for name in add_links:
		y=name.replace("/mediawiki/index.php/","")
		dump.write(y+"\n")

with open("temp1.txt") as f:
	for line in f:					
		process(line)
		dump_urls()	





#FOr Unique list
#$ cat sample.txt | sort | uniq > output.txt