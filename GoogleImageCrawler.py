# -*- coding: utf-8 -*-
"""
Platform: windows 10
Running environment: Python 2.7

Created on Sun Dec 25 2016
@author: luckycallor(www.luckycallor.com)
"""

from selenium import webdriver
import threading
import socket
import urllib
import os

'''
Func@getIMGurlsGoogle:
	输入一组搜索关键词，函数爬取相关的图片url并保存到指定目录下以关键词命名的文件夹中
	Parameters：
		search_items：list，包含搜索关键词
		num：int，每个关键词最多爬取的图片数量
		bottom：int，页面下拉时，控制下拉的最底部位置，也能起到控制爬取数量的作用
		saveDIR：string，图片url保存目录
		items_per_round：int，每次重启浏览器，搜索的关键词数量
'''

def getIMGurlsGoogle(search_items,num,bottom,saveDIR,items_per_round):
    if(os.path.exists(saveDIR) == False):
        os.mkdir(saveDIR)
    driver = webdriver.Firefox()
    driver.maximize_window()
    threshold = items_per_round - 1
    item_cnt = 0
    for search_item in search_items:
        if(item_cnt%items_per_round == threshold):
            driver.quit()
            driver = webdriver.Firefox()
            driver.maximize_window()
        print '#%d: %s' % (item_cnt, search_item)
        search_item = search_item.split(' ')
        search_item = '+'.join(search_item)
        search_url = 'https://www.google.com/search?aq=f&tbm=isch&q=%s' % search_item
        img_url_set = set()
        driver.get(search_url)
        pos = 0
        cnt = 0
        ans = []
        while(True):
            if((cnt >= num) or (pos >= bottom)):
                break
            js = "document.documentElement.scrollTop=%d" % pos
            driver.execute_script(js)
            for element in driver.find_elements_by_tag_name('a'):  
                href_ori = element.get_attribute('href')
                if(href_ori == None):
                    continue
                href_decoded = urllib.unquote(href_ori)
                if(href_decoded.find('imgres?imgurl=http') < 0):
                    continue
                img_url =  href_decoded[href_decoded.find('imgurl=')+len('imgurl='):href_decoded.find('&imgrefurl')]
                if(img_url not in img_url_set):
                    img_url_set.add(img_url)
                    ans.append(img_url)
                    cnt += 1
                    if(cnt >= num):
                        break
            pos += 600
        f = open(saveDIR + '\\' + search_items[item_cnt] + '.txt', 'w')
        for u in ans:
            f.write(u)
            f.write('\n')
        f.close()
        item_cnt += 1
    driver.quit()

'''
Func@getIMG:
	根据图片url将图片下载到本地
	Parameters：
		fns：list，保存有图片url的文件的文件名的集合
		readDIR：string，fns中文件所在目录
		saveDIR：string，下载图片的保存目录
'''

def getIMG(fns,readDIR,saveDIR):
    if(os.path.exists(saveDIR) == False):
        os.mkdir(saveDIR)
    for fn in fns:
        name = fn[:-4]
        if(os.path.exists(saveDIR + '\\' + name) == False):
            os.mkdir(saveDIR + '\\' + name)
        furl = open(readDIR + '\\' + fn)
        count = 0
        for url in furl.readlines():
            count += 1
            socket.setdefaulttimeout(120)
            try:
                urllib.urlretrieve(url, saveDIR + '\\' + name + '\\%d.jpg' % count)
            except:
                continue
            print 'Downloading: %s ---- #%d' % (name,count)

'''
Func@getIMG_mt:
	多线程版本的图片下载函数
	Paramdters：
		num_t：int，开启的线程数量
		readDIR：string，保存图片url的文件所在目录
		saveDIR：string，下载图片的保存目录
'''

def getIMG_mt(num_t,readDIR,saveDIR):
    if(num_t <= 0):
        num_t = 1
    fns = os.listdir(readDIR)
    total_num = len(fns)
    avg = total_num / num_t
    left = total_num % num_t
    threads = []
    cur_idx = 0
    for i in range(left):
        t = threading.Thread(target=getIMG,args=(list(fns[cur_idx:cur_idx+avg+1]),readDIR,saveDIR))
        threads.append(t)
        cur_idx += avg+1
    for i in range(num_t-left):
        t = threading.Thread(target=getIMG,args=(list(fns[cur_idx:cur_idx+avg]),readDIR,saveDIR))
        threads.append(t)
        cur_idx += avg
    
    for i in range(num_t):
        threads[i].start()
    
    for i in range(num_t):
        threads[i].join()

if __name__ == '__main__':
    # example:
    url_saveDIR = r'G:\myDIR\urls'
    img_saveDIR = r'G:\myDIR\images'
    search_items = ['Scarlett Johansson', 'Benedict Cumberbatch']
    getIMGurlsGoogle(search_items = search_items, num = 100,bottom = 10000,saveDIR = url_saveDIR,items_per_round = 10)
    getIMG_mt(num_t = 2,readDIR = url_saveDIR,saveDIR = img_saveDIR)
