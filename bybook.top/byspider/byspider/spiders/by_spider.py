# -*- coding: utf-8 -*-
import scrapy
from byspider.items import ByspiderItem
from bs4 import BeautifulSoup
import time
import re

import requests


class BySpiderSpider(scrapy.Spider):
    name = 'by_spider'
    allowed_domains = ['bybook.top']
    start_urls = ['http://bybook.top/']

    # 保存爬取到的 category 字段到 set 中 （set不重复）
    category_set = set()

    # 标记共爬取的 目录页 数
    book_menu_cnt = 0
    # 标记共爬取的 图书详情页 数
    book_detail_cnt = 0

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        '''
        if self.book_detail_cnt > 10:
            return
        '''
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

        print('book_menu_cnt: ' + str(self.book_menu_cnt))
        print('book_detail_cnt: ' + str(self.book_detail_cnt))

        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

        time.sleep(0.5)
        for a in soup.select('a'):
            try:
                new_url = a['href']
                # 图书 目录 URL
                if re.match(r'http.?://bybook.top/category/.*', new_url):
                    print('找到一个 category url:')
                    print(new_url)
                    self.book_menu_cnt += 1
                    yield response.follow(new_url, callback = self.parse)

                # 图书 详情页 URL 
                elif re.match(r'http.?://bybook.top/.*/.*/[0-9][0-9]*/', new_url):
                    print('找到一个 book_detail_url:')
                    print(new_url)
                    self.book_detail_cnt += 1
                    # yield response.follow(new_url, callback = self.parse_detail)
                    yield scrapy.FormRequest(new_url, formdata = { 'huoduan_verifycode': '1902' }, callback = self.parse_detail)
                    '''
                    return [FormRequest(url = new_url,
                                        formdata = { 'huoduan_verifycode': '1902'},
                                        callback = self.parse_detail)]
                    '''
                else:
                    pass
            except Exception as e:
                pass

    # 从 目录页 中提取 详情页 URL
    def get_url_from_menu(self, response):
        pass

    def parse_detail(self, response):
        time.sleep(1)
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            print('\n正在解析：')
            print(soup.title.text.strip())

            detail_content = soup.select("div.kratos-hentry")[0]

            title = self.extract_title(detail_content)
            if not title:
                return
            pic = self.extract_pic(detail_content)
            author = self.extract_author(detail_content)
            rating = self.extract_rating(detail_content)
            category = self.extract_category( response.url )
            infos = self.extract_infos(detail_content)
            description = self.extract_description(detail_content)
            pan_1 = self.extract_pan_1(detail_content)
            if not pan_1:
                return
            pan_2 = self.extract_pan_2(detail_content)
            pan_3 = self.extract_pan_3(detail_content)
            pan_pass = self.extract_pass(detail_content)
            origin = response.url

            # 创建 book_item 并 yield 输出
            book_item = ByspiderItem()

            book_item['title'] = title
            book_item['pic'] = pic
            book_item['author'] = author
            book_item['rating'] = rating
            book_item['category'] = category
            book_item['infos'] = infos
            book_item['description'] = description
            book_item['pan_1'] = pan_1
            book_item['pan_2'] = pan_2
            book_item['pan_3'] = pan_3
            book_item['pan_pass'] = pan_pass
            book_item['origin'] = origin
            yield book_item
        except Exception as e:
            print('\n解析详情页 失败 跳过')
            print(e)

    # 从 图书详情页 提取 图书名
    def extract_title(self, soup):
        try:
            title = soup.header.h1.text.replace('  ','').strip()
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
        return '请参考图书详情'


    # 从 图书详情页 提取 图书 评分
    def extract_rating(self, soup):
        try:
            rating = soup.strong.text[5:].strip()
            return rating
        except Exception as e:
            print('提取 图书 rating 失败')
            return '0.0'

    # 从 图书详情页 提取 图书 分类
    def extract_category(self, url):
        try:
            tags = url.split('/')
            category = tags[3] + '-' + tags[4]
            # 将 提取到的 catogory 添加到 self.category_set
            self.category_set.add(category)
            # 写入 self.category_set 到文件           
            self.save_category_set()
            return category
        except Exception as e:
            print('提取 图书 category 失败')
            print(e)
            return '其它'

    # 从 图书详情页 提取 图书 infos
    def extract_infos(self, soup):
        '''
        try:
            infos = soup.select("p")[3].text
            return infos
        except Exception as e:
            print('提取 图书 infos 失败')
            return ''
        '''
        return '暂无'

    # 从 图书详情页 提取 图书description 
    def extract_description(self, soup):
        try:
            description = soup.select('div.kratos-post-content')[0].select('p')[2].text
            return description
        except Exception as e:
            print('提取 图书 description 失败')
            return '暂无'

    # 从 图书详情页 提取 图书 网盘链接 1
    def extract_pan_1(self, soup):
        try:
            tmp_url = soup.select('div.xydown_down_link')[0].a['href']
            real_url = self.get_real_pan(tmp_url)
            if real_url:
                pan_1 = '百度网盘##' + real_url
                return pan_1
            else:
                return None
        except Exception as e:
            print('提取 图书 pan_1 失败')
            return None

    # 工具函数
    # 从网盘跳转页面 获取真实 网盘地址
    def get_real_pan(self, url):
        try:
            r = requests.get(url, timeout = 30)
            soup = BeautifulSoup(r.text, 'lxml')
            real_url = soup.a['href']
            if len(real_url):
                return real_url
            else:
                return None
        except Exception as e:
            print('获取 get_real_pan 失败')
            print(e)
            return None

    # 从 图书详情页 提取 图书 网盘链接 2
    # 本网站当前只有 一个 网盘链接，故 此函数 暂时不需要
    def extract_pan_2(self, soup):
        return ''

    # 从 图书详情页 提取 图书 网盘链接 3
    # 本网站当前只有 一个 网盘链接，故 此函数 暂时不需要
    def extract_pan_3(self, soup):
        return ''

    # 从 图书详情页 提取 图书 网盘提取码
    # 该网站 当前没有设置 提取码，故返回 空字符串
    def extract_pass(self, soup):
        passwd = ''
        try:
            passwd = soup.select('div.kratos-post-content')[0].select('div')[1].text.strip()
        except Exception as e:
            pass
        return passwd

    # 输出 self.category_set 到文件
    def save_category_set(self):
        file_name = 'category_set.txt'
        with open(file_name, 'w') as f:
            for category in self.category_set:
                f.write(category)
                f.write('\n')
        print('输出 self.category_set 到文件完成')
        print(file_name)
        print()
        print()

