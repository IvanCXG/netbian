# coding=utf-8
import re
import urllib.request
import time
import os
import threading

class Netbian():
    #获取页面内容并返回
    def get_html(self,url):
        # header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'}
        # request = urllib.request.Request(url=url,headers=header,method='POST')
        # html_text = urllib.request.urlopen(request).read().decode('gb18030')
        html_= urllib.request.urlopen(url)
        html_text = html_.read().decode('gb18030')
        time.sleep(0.1)
        return html_text
    #获取对应正则表达式要爬取的内容并返回
    def get_special(self,html_text,reg):
        special_text = re.findall(reg,html_text)
        return special_text

    #壁纸保存路径
    def save_path(self,path):
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            print(path + '  已存在！')

    #判断每个壁纸分类是否存下一页，并获取每一页中的img名称和数量，直到没有下一页时推出
    def get_next_page(self,url,n,page_url):
        html_text = self.get_html(url)
        #判断是否有下一页，并获取下一页的URL
        next_page_reg = re.compile('下一页')
        next_page_flag = self.get_special(html_text,next_page_reg)

        while next_page_flag == ['下一页']:
            n += 1
            next_page_url = first_page_url+ '/index_%d.htm' % n
            page_url.append(next_page_url)
            #print(next_page_url)
            #print(n)
            if next_page_flag == []:
                continue
            return self.get_next_page(next_page_url, n,page_url)
        return page_url

    thread_lock = threading.BoundedSemaphore(value=20)
    def download(self,url,path,name):
        urllib.request.urlretrieve(path,path+'/%s.jpg' % name)
        self.thread_lock.release()





if __name__ == '__main__':
    url = 'http://www.netbian.com/'
    nb = Netbian()
    root_path = 'E:/netbian.com'
    nb.save_path(root_path)

    first_html_text = nb.get_html(url)
    #获取首页中有多少分类，以及对应的URL,对应的名称
    #types_reg = re.compile(r'<a href="/?\w?/\w+/" title="(.+?)"|target="_blank">[\u4e00-\u9fa5]</a>')
    types_reg = re.compile(r'<a href="/(\w+)/" title="(.+?)">.+?</a>')
    bizi_type_name = nb.get_special(first_html_text,types_reg)
    #print(bizi_type_name)
    types_num = len(bizi_type_name)
    for i in range(0,types_num):
        first_page_url = url+bizi_type_name[i][0]
        n = 1
        #print(first_page_url)
        sec_path = root_path +'/'+ bizi_type_name[i][1]
        #print(sec_path)
        #创建二级路径
        nb.save_path(sec_path)

        # 判断每个壁纸分类是否存下一页，并获取每一页中的img名称和数量
        each_page_url = nb.get_next_page(first_page_url,n,page_url=[])
        #将首页URL插入到list中
        each_page_url.insert(0,first_page_url)
        #print(each_page_url)
        page_num = len(each_page_url)
        print(page_num)
        for j in range(0,page_num):
            page_html_text = nb.get_html(each_page_url[j])
            #获取每个page中有多少张图片,以及url_and_name
            url_and_name_reg = re.compile(r'<a href="/(\w+/\d+)\.htm" title="(.+?)" target="_blank">')
            url_and_name = nb.get_special(page_html_text,url_and_name_reg)
            img_url_num = len(url_and_name)
            #print(url_and_name)
            #print(img_url_num)
            for k in range(0,img_url_num):
                img_url_virtual = url + '/%s-1920x1080.htm' % url_and_name[k][0]
                #print(img_url_virtual)
                img_html_text = nb.get_html(img_url_virtual)
                img_reg = re.compile(r'<img src="(.+?)" title="(.+?)" alt=".+?" />')
                img_url1 = nb.get_special(img_html_text,img_reg)
                #img_path  = sec_path+'/%s.jpg' % img_url[0][1]

                if img_url1 ==[]:
                    print('第%d个分类第%d页第%d张1920x1080像素壁纸不存在！' % ((i + 1), (j + 1), (k + 1)))
                    #print(img_url)
                if img_url1 != []:
                    img_name = eval(repr(img_url1[0][1]).replace('\\','@'))
                    #print(img_url)
                    try:
                        if not os.path.isfile(sec_path+'/%s.jpg' % img_name):
                            nb.thread_lock.acquire()
                            t = threading.Thread(target=nb.download,args=(img_url1[0][0],sec_path,img_name))
                            t.start()
                            #nb.download(img_url1[0][0],sec_path,img_name)
                            #urllib.request.urlretrieve(img_url1[0][0],sec_path+'/%s.jpg' % img_name)
                            print('第%d个分类第%d页第%d张壁纸下载成功！共%d张' % ((i+1),(j+1),(k+1),(img_url_num*j+k+1)))
                        else:
                            print('第%d个分类第%d页第%d张壁纸已存在！共第%d张壁纸' % ((i+1),(j+1),(k+1),(img_url_num*j+k+1)))
                    except Exception as e:
                        print(e)




