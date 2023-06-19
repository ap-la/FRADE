import urllib2
from bs4 import BeautifulSoup
from pprint import pprint
import numpy as np
import random, string
import os
from PIL import Image

img_src="/var/www/html/imgur/gallery/temporary/image.png"
src="/var/www/html/imgur/dummy.html"
path_str="/var/www/html/imgur/"
topics=['Delta_Dawn', 'Phi_Sigma_Tau', 'AntiOxidant','Healthy_Wealthy','Water', 'iPhone','Blanket', 'Chlorex','Ted_Talk','Amazon','Station','Sensors', 'House','Supernatural']
folder_name=["Feedback","Database", "Reviews","Comments","Exclusive", "News_Feed","Fruit_new","San_Andreas","Cary","Brian","Taylor_Swift","Adam","Tarzan","Santa",'Nelson','Jacob']
extra=['-check','-new','-revised', '-feed','-review','-print','-copy','-uplink','-description','-change','-analyse','-opt','-unit','-o','-u','-w','-j','p','new']
word=['Star_Trek','More', 'About','Clear','Discuss','Forum','Notes','Admin','Important','Scan','Peace','Home-Decor','Yoga','Plot','Kindle','Summer','Spring','Pluto']
true_false=['true','false']
size=[1,2,3]
chars=string.ascii_lowercase + string.ascii_uppercase + string.digits

def make_img():
   n=int(random.choice(size))
   m=int(random.choice(size))
   image=Image.new('RGB',(n,m))
   image.save(img_src, "PNG")





fd = open('safe.html', 'r')
data = fd.read()
fd.close()
soup = BeautifulSoup(data,"lxml")


all_div=[]
for div in soup.find_all('div'):
        all_div.append(div)


no_of_links=len(soup.find_all('a'))

def randomword(length):
   return ''.join(random.choice(chars) for i in range(length))


all_links=[]
web_links=[]
ar=[]
directory=[]
for link in soup.find_all('a'):
   all_links.append((link.get('href')))
for l in all_links:
   if l.startswith("//imgur"):
      str="//imgur.human.frade.emulab.net"
      x= l.split(str)[1]
      if x!= "":
         web_links.append(x)
   elif l.startswith("/"):
      web_links.append(l)

        #pprint(web_links)
unique_links=np.unique(web_links)
        #pprint(unique_links)
for ul in unique_links:
   s="/"
   chopped_link=ul.split(s)
   ar.append(chopped_link[1])
                                #print chopped_link
directory=np.unique(ar)
def make_link():
        name= random.choice(directory)
      #  print name
        directory_name=path_str+name
        if (os.path.isdir(directory_name)):
                if name=="gallery":
                       y= randomword(6)
                       href="/"+name+"/"+y
                       link_name=directory_name+"/"+y
                       print href
                       return link_name,href
                if name=="topic" or name=="user":
                       y=random.choice(topics)
                       href="/"+name+"/"+y
                       link_name=directory_name+"/"+y
                       return link_name,href
                else:
                       y= random.choice(folder_name)
                       href="/"+name+"/"+y
                       link_name=directory_name+"/"+y
                       return link_name,href

def make_symlink():
        new_link,href=make_link()
        #print new_link,href
if os.path.islink(new_link):
                pass
        else:
                os.symlink(src,new_link)
        return new_link,href



# Add links to the page
def addlinks(link):
  temp_soup=BeautifulSoup(link,"html.parser")
  test_div=random.choice(all_div)
  test_div.append(temp_soup)

# get id name and title to make the link look like original link
id_name_list=[]
title_name_list=[]
def get_the_name():
   for link in soup.findAll('a'):
        if link.has_attr('id'):
           id_name_list.append(link['id'])
        if link.has_attr('title'):
           title_name_list.append(link['title'])

config_file=open('/var/www/html/config_file.txt','r')
ratio=int(config_file.readline())
config_file.close()
get_the_name()
#print ratio

make_img()

limit=int(no_of_links/ratio)
for i in range(1,int(limit/3)):
        id_name=random.choice(id_name_list)
        title_name=random.choice(title_name_list)
        new_link, href=make_symlink()
        link='<a data-show-count="'+random.choice(true_false)+'" style="font-size:0" id="'+id_name+random.choice(extra)+'" title="'+title_name+'" href="'+href+'">'+random.choice(word)+'</a>'
 #      print link
        addlinks(link)


for i in range(1,int(limit/3)):
        id_name=random.choice(id_name_list)
        title_name=random.choice(title_name_list)
        new_link, href=make_symlink()
link='<a data-show-count="'+random.choice(true_false)+'" style="font-size:0" id="'+id_name+random.choice(extra)+'" title="'+title_name+'" href="'+href+'">'+random.choice(word)+'</a>'
 #      print link
        addlinks(link)


for i in range(1,int(limit/3)):
        id_name=random.choice(id_name_list)
        title_name=random.choice(title_name_list)
        new_link, href=make_symlink()
        link='<a data-show-count="'+random.choice(true_false)+'" id="'+id_name+random.choice(extra)+'" title="'+title_name+'" href="'+href+'"></a>'
  #      print link
        addlinks(link)

for i in range(1,int(limit/3)):
        id_name=random.choice(id_name_list)
        title_name=random.choice(title_name_list)
        new_link, href=make_symlink()
        link='<a data-show-count="false" id="'+id_name+random.choice(extra)+'" title="'+title_name+'" href="'+href+'"><img src="'+img_src+'"></a>'
   #     print link
        addlinks(link)


file('index.html','w').write(soup.encode('utf-8'))

