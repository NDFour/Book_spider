# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from book_spider.items import BookSpiderItem, Href_Pic_Item
import time
import re
import requests


class A52bookSpider(scrapy.Spider):
    name = '52book'
    allowed_domains = ['52book.me']
    start_urls = ['http://www.52book.me/page/1/']

    now_page = '1'
    # total_page = 7960
    total_page = 7960
    base_url = 'http://www.52book.me/page/'

    # Server 酱 / 微信提醒 URL
    wechat_url = 'https://sc.ftqq.com/****.send'
    # Server 酱 消息题
    notify_data = {
        'text':'我是标题',
        'desp':'我是内容',
    }

    # 从目录页中提取 图书详情页 URL
    def parse(self, response):
        # 先微信通知
        '''
        self.notify_data['text'] = '52book_spider 开始运行'
        self.notify_data['desp'] = '开始运行'
        self.wechat_notify()
        '''

        print('\n## 开始解析第 ' + self.now_page + ' 页 ##')
        print('当前解析的目录页是：')
        print(response.url)
        # 防止爬取过快给 服务器造成压力
        time.sleep(0.2)

        '''
        file_name = './' + response.url.replace('/', '#') + '.html'
        with open( file_name, 'w') as f:
            f.write(response.text)
        '''

        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')
        for book in soup.select("article"):
            href = book.div.a['href']
            # 解析详情页 信息
            yield scrapy.Request(href, callback = self.parse_detail)
        # 重新爬取 封面图
        '''
        for book in soup.select("article"):
            try:
                href = book.div.a['href']
                # 补充 封面图
                pic = book.div.a.img['data-src']
                href_pic_item = Href_Pic_Item()
                href_pic_item['href'] = href
                href_pic_item['pic'] = pic
                yield href_pic_item
            except Exception as e:
                print('该项 无 封面图')
                print(e)
        '''
        # 重新爬取 封面图 END

        next_page = int(self.now_page) + 1
        self.now_page = str(next_page)
        next_page_url = self.base_url + str(next_page)
        # 每隔 500 页发送一次微信通知
        if int(self.now_page) % 500 == 0:
            # 先微信通知
            self.notify_data['text'] = '52book_spider 已爬取 ' + self.now_page + ' 目录'
            self.notify_data['desp'] = '已爬取 ' + self.now_page + ' 共有 ' + str(self.total_page)
            # self.wechat_notify()
        if int(self.now_page) > self.total_page:
            # 先微信通知
            self.notify_data['text'] = '52book_spider 目录爬取结束'
            self.notify_data['desp'] = '结束运行'
            # self.wechat_notify()

            print('\n\n结束，已爬取 ' + self.now_page + ' 页')
            return

        yield scrapy.Request(next_page_url, callback = self.parse)

    # 解析 图书详情页 信息
    def parse_detail(self, response):
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')

        print('\n正在解析：')
        print(soup.title.text)

        book_item = BookSpiderItem()

        book_item['title'] = self.extract_title(soup)
        book_item['catogory'] = self.extract_catogory(soup)
        book_item['infos'] = self.extract_infos(soup)

        # print('catogory:' + self.extract_catogory(soup))

        pic = self.extract_pic(response)
        if len(pic):
            book_item['pic'] = pic

        book_item['origin'] = response.url

        pan_url = self.extract_pan(soup)
        if len(pan_url):
            print('pan_url:[' + pan_url + ']')
            # book_item['pan_1'] =  pan_url
            # print('pan_1:' + pan_url)
            print('开始解析真实 网盘地址')
            yield scrapy.Request(pan_url, callback = self.extract_pan_from_52book, meta = {'book_item': book_item} )
            # yield scrapy.Request(pan_url, callback = self.extract_pan_from_52book)
        else:
            print('pan_url:[' + pan_url + ']')
            # 如果没有解析到 网盘链接，直接退出，不保存该数据
            return


    # 从 图书详情页 提取标题
    def extract_title(self, soup):
        # return soup.h3.text
        return soup.title.text[:-7]

    # 从 图书详情页 catogory
    def extract_catogory(self, soup):
        catogory = ''
        try:
            catogory = soup.find_all(rel='category')[0].text
        except Exception as e:
            print('提取 catogory 失败')
            catogory = '未分类'
        return catogory

    # 从 图书详情页 提取 封面图
    def extract_pic(self, response):
        pic = ''
        try:
            tmp = re.search(r'content="http://www.52book.me/wp-content/uploads.*?g', response.text)
            if tmp:
                pic = tmp[0][9:]
            else:
                print('未提取到 pic')
                pic = ''
        except Exception as e:
            print('提取 pic 失败')
            pic = ''
        return pic

    # 从 图书详情页 infos
    def extract_infos(self, soup):
        infos = ''
        try:
            infos = soup.select("div.entry-content")[0].p.text[:-4]
        except Exception as e:
            print('提取 infos 失败')
            infos = '暂无简介'
        return infos
    
    # 从 图书详情页 pan_1
    def extract_pan(self, soup):
        pan_1 = ''
        try:
            # 需要先请求这个 URL ，302 重定向得到 城通网盘 URL
            chengtong = 'http://www.52book.me' + soup.select("div.entry-content")[0].a['href']
            # pan_1 = requests.get(chengtong, timeout = 30).url
            # return '城通云盘##' + pan_1
            return chengtong
        except Exception as e:
            print('提取 pan_1 失败')
            print(e)
            print('###########')
            return ''

    # 将 图书详情页 获得的 pan URL 半成品 提取成 完整 城通网盘地址
    def extract_pan_from_52book(self, response):
        print('进入 extract_pan_from_52book')

        book_item = response.meta.get('book_item')
        if book_item:
            book_item['pan_1'] = '城通云盘##' + response.url

            # print('----------------- book_item:')
            # print(book_item)

            yield book_item
        else:
            print('获取 book_item 失败')
            return

    # 发送微信消息提醒
    def wechat_notify(self):
        r = requests.get( self.wechat_url, params = self.notify_data, timeout = 10 )
