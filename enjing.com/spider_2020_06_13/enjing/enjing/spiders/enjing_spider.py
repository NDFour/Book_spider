# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import re
import requests
from enjing.items import EnjingItem
import time


class EnjingSpiderSpider(scrapy.Spider):
    name = 'enjing_spider'
    allowed_domains = ['enjing.com']
    start_urls = ['http://enjing.com/']

    detail_cnt = 0

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        for a in soup.select('a'):
            # 图书详情页
            if re.match(r'https://www.enjing.com/.*?/[0-9]*?.htm', a['href']):
                yield scrapy.Request(a['href'], callback=self.parse_detail )
            # 分类标签
            elif re.match(r'https://www.enjing.com/tag/.*?/', a['href']):
                yield scrapy.Request(a['href'], callback=self.parse )
            else:
                pass

    # 解析详情页 信息
    def parse_detail(self, response):

        time.sleep(0.5)

        try:
            soup = BeautifulSoup(response.text, 'lxml')

            title = self.extract_title(soup)
            pic = self.extract_pic(soup)
            author = self.extract_author(soup)
            rating = self.extract_rating(soup)
            category = self.extract_category(soup)
            infos = self.extract_infos(soup)
            description = self.extract_description(soup)

            # 下载页面链接
            down_url = soup.select('a.downbtn')[0]['href']

            pan_url = self.parse_downbtn(down_url)
            pan_1 = pan_url[0]
            pan_2 = pan_url[1]
            pan_3 = pan_url[2]
            pan_valid = len(pan_1) + len(pan_2) + len(pan_3)
            if not pan_valid:
                print('pan_valid = ' + str(pan_valid))
                return
            
            pan_pass = ''
            origin = response.url

            new_item = EnjingItem()
            new_item['title'] = title
            new_item['author'] = author
            new_item['rating'] = rating
            new_item['category'] = category
            new_item['infos'] = infos
            new_item['description'] = description
            new_item['pic'] = pic
            new_item['pan_1'] = pan_1
            new_item['pan_2'] = pan_2
            new_item['pan_3'] = pan_3
            new_item['pan_pass'] = pan_pass
            new_item['origin'] = origin

            yield new_item

        except Exception as e:
            print('解析详情页失败')
            return




    '''
    以下为工具函数，与scrapy无关
    '''


    # 从下载页面 解析下载地址
    '''
    input: donw-btn page url

    output: a list of 3 format download urls
    '''
    def parse_downbtn(self, url):

        print('detal_cnt: ' + str(self.detail_cnt))
        self.detail_cnt += 1

        pan_url = []
        try:
            r = requests.get(url, timeout = 30)
            soup = BeautifulSoup(r.text, 'lxml')

            for a in soup.select('div.download-text')[0].select('a'):
                pan_url.append( a.text + '##' + a['href'] )
            
        except Exception as e:
            print('解析下载页面失败')

        finally:

            while len(pan_url) < 3:
                pan_url.append('')
            
            return pan_url





    # 从 图书详情页 提取 图书名
    def extract_title(self, soup):
        try:
            title = soup.select('div.main-wrap')[0].h1.text.strip()
            return title
        except Exception as e:
            print('提取 图书 title 失败')
            return None

    # 从 图书详情页 提取 图书 封面图
    def extract_pic(self, soup):
        try:
            pic = soup.img['src']
            return pic
        except Exception as e:
            print('提取 图书 pic 失败')
            return None


    # 从 图书详情页 提取 图书 作者
    def extract_author(self, soup):
        try:
            author = soup.select('div.book-describe')[0].p.text.strip().replace('作者：', '')
            return author
        except Exception as e:
            return '请参考图书详情'


    # 从 图书详情页 提取 图书 评分
    def extract_rating(self, soup):
        try:
            rating = soup.select('div.book-describe')[0].select('p')[-1].span.text.strip()
            return rating
        except Exception as e:
            return '0.0'

    # 从 图书详情页 提取 图书 分类
    def extract_category(self, soup):
        try:
            category =  soup.select('div.book-describe')[0].select('p')[1].a.text.strip()
            return category
        except Exception as e:
            return '其它'

    # 从 图书详情页 提取 图书 infos
    def extract_infos(self, soup):
        try:
            infos = soup.select('div.book-describe')[0].text
            return infos
        except Exception as e:
            return '暂无'

    # 从 图书详情页 提取 图书description 
    def extract_description(self, soup):
        try:
            description = soup.select('div.describe')[0].text.replace('下载 地址', '').replace('下载地址', '')
            return description
        except Exception as e:
            return '暂无'


