# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from sobooks.items import SobooksItem
import time
import re
import requests


class SobooksSpiderSpider(scrapy.Spider):
    name = 'sobooks_spider'
    allowed_domains = ['sobooks.cc']
    start_urls = ['https://sobooks.cc/page/2']

    now_page = '2'
    base_url = 'https://sobooks.cc/page/'

    # 从目录页中提取 图书详情页 URL
    def parse(self, response):
        print('\n当前解析的目录页是：')
        print(response.url)

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

        next_page = int(self.now_page) + 1
        self.now_page = str(next_page)
        next_page_url = self.base_url + str(next_page)
        if int(self.now_page) > 3:
            return

        yield scrapy.Request(next_page_url, callback = self.parse)

    # 解析 图书详情页 信息
    def parse_detail(self, response):
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')

        print('\n正在解析：')
        print(soup.title.text)

        # 解析到的 book 信息列表
        bookItems = []
        book_item = BookSpiderItem()

        book_item['title'] = self.extract_title(soup)
        book_item['catogory'] = self.extract_catogory(soup)
        book_item['infos'] = self.extract_infos(soup)

        print('catogory:' + self.extract_catogory(soup))

        pic = self.extract_pic(response)
        if len(pic):
            book_item['pic'] = pic

        pan_url = self.extract_pan(soup)
        if len(pan_url):
            book_item['pan_1'] =  pan_url
            print('pan_1:' + pan_url)

        book_item['origin'] = response.url

        bookItems.append(book_item)
        yield book_item

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
            infos = soup.select("div.entry-content")[0].p.text
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
            pan_1 = requests.get(chengtong, timeout = 30).url
            return '城通云盘##' + pan_1
        except Exception as e:
            print('提取 pan_1 失败')
            print(e)
            print('###########')
            return ''
