# -*- coding: utf-8 -*-
import scrapy
import requests
from bs4 import BeautifulSoup
import time
from kindle8.items import Kindle8Item


class Kindle8SpiderSpider(scrapy.Spider):
    name = 'kindle8_spider'
    allowed_domains = ['kindle8.cc']
    start_urls = ['https://www.kindle8.cc/zzjj']

    # 小说文学 分类
    base_url = 'https://www.kindle8.cc/qtsj/page/'
    # 当前正在爬取的 page 页数
    now_page = 1
    # 总共需要爬取的页数
    total_page = 16
    # 保存爬取到的 category 字段到 set 中 （set不重复）
    category_set = set()

    # 解析目录页 中的 详情页 URL
    def parse(self, response):
        print('\n## 开始解析第 ' + str(self.now_page) + ' 页 ##')
        print('当前解析的目录页是：')
        print(response.url)

        # 提取图书详情页 URL
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            book_main = soup.select("section")[0]

            print('本目录页共有 ' + str(len(book_main.select("article"))) + ' 本书' )
            for book in book_main.select("article"):
                href = book.a['href']
                # 获取详情页信息
                yield scrapy.FormRequest(href, formdata = { 'huoduan_verifycode': '0101' }, callback = self.parse_detail)

        except Exception as e:
            print('从目录页 提取 详情页 失败')
            print(e)
            print()

        # 构造下一页目录 URL 并访问解析
        '''
        next_page = self.now_page + 1
        self.now_page = next_page
        next_page_url = self.base_url + str(next_page)
        if self.now_page > self.total_page:
            print('\n\n结束，已爬取 ' + str(self.now_page) + ' 页')
            return

        yield scrapy.Request(next_page_url, callback = self.parse)
        '''

    def test_pass(self):
        print('********** 我是一只小脑腐')

    # 解析详情页 提取各项信息
    def parse_detail(self, response):
        # time.sleep(1)
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            print('\n正在解析：')
            print(soup.title.text.strip())

            detail_content = soup.article

            title = self.extract_title(soup)
            if not title:
                return
            pic = self.extract_pic(detail_content)
            author = self.extract_author(detail_content)
            rating = self.extract_rating(detail_content)
            category = self.extract_category( soup.select("div#breadcrumbs")[0] )
            infos = self.extract_infos(detail_content)
            description = self.extract_description(detail_content)
            pan_1 = self.extract_pan_1(detail_content)
            pan_2 = self.extract_pan_2(detail_content)
            pan_3 = self.extract_pan_3(detail_content)
            pan_pass = self.extract_pass(detail_content)
            origin = response.url

            # 创建 book_item 并 yield 输出
            book_item = Kindle8Item()

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
            title = soup.title.text[:-29]
            return title
        except Exception as e:
            print('提取 图书 title 失败')
            return None

    # 从 图书详情页 提取 图书 封面图
    def extract_pic(self, soup):
        try:
            pic = soup.div.img['src']
            return pic
        except Exception as e:
            print('提取 图书 pic 失败')
            return None


    # 从 图书详情页 提取 图书 作者
    def extract_author(self, soup):
        return '请参考图书详情'


    # 从 图书详情页 提取 图书 评分
    def extract_rating(self, soup):
        return ''

    # 从 图书详情页 提取 图书 分类
    def extract_category(self, soup):
        try:
            category = soup.select("a")[1].text
            # 将 提取到的 catogory 添加到 self.category_set
            self.category_set.add(category)
            # 写入 self.category_set 到文件           
            self.save_category_set()
            return category
        except Exception as e:
            print('提取 图书 category 失败')
            print(e)
            return ''

    # 从 图书详情页 提取 图书 infos
    def extract_infos(self, soup):
        try:
            infos = soup.select("div.entry-content")[0].select("p")[2].text
            return infos
        except Exception as e:
            print('提取 图书 infos 失败')
            return ''

    # 从 图书详情页 提取 图书description 
    def extract_description(self, soup):
        try:
            description = soup.select("div.entry-content")[0].select("p")[1].text
            return description
        except Exception as e:
            print('提取 图书 description 失败')
            return ''

    # 从 图书详情页 提取 图书 网盘链接 1
    def extract_pan_1(self, soup):
        try:
            # pan_1 = '城通网盘##' + soup.select("p")[4].a['href']
            file_name = soup.select("div")[0].div.a.text[-4:].strip()
            file_url = requests.get(soup.select("div")[0].div.a['href'], timeout = 20).url
            pan_1 = file_name + '##' + file_url
            return pan_1
        except Exception as e:
            print('提取 图书 pan_1 失败')
            print(e)
            return ''

    # 从 图书详情页 提取 图书 网盘链接 2
    # 本网站当前只有 一个 网盘链接，故 此函数 暂时不需要
    def extract_pan_2(self, soup):
        try:
            # pan_2 = '城通网盘##' + soup.select("p")[4].a['href']
            file_name = soup.select("div")[0].div.select("a")[1].text[-4:].strip()
            file_url = requests.get(soup.select("div")[0].div.select("a")[1]['href'], timeout = 20).url
            pan_2 = file_name + '##' + file_url
            return pan_2
        except Exception as e:
            print('提取 图书 pan_2 失败')
            print(e)
            return ''       

    # 从 图书详情页 提取 图书 网盘链接 3
    # 本网站当前只有 一个 网盘链接，故 此函数 暂时不需要
    def extract_pan_3(self, soup):
        try:
            # pan_3 = '城通网盘##' + soup.select("p")[4].a['href']
            file_name = soup.select("div")[0].div.select("a")[2].text[-4:].strip()
            file_url = requests.get(soup.select("div")[0].div.select("a")[2]['href'], timeout = 20).url
            pan_3 = file_name + '##' + file_url
            return pan_3
        except Exception as e:
            print('提取 图书 pan_3 失败')
            print(e)
            return ''       

    # 从 图书详情页 提取 图书 网盘提取码
    # 该网站 当前没有设置 提取码，故返回 空字符串
    def extract_pass(self, soup):
        return ''

    # 输出 self.category_set 到文件
    def save_category_set(self):
        file_name = '/Users/lynn/Desktop/好书分享君/Book_spider/kindle8.cc/kindle8/category_set.txt'
        with open(file_name, 'w') as f:
            for category in self.category_set:
                f.write(category)
                f.write('\n')
        print('输出 self.category_set 到文件完成')
        print(file_name)
        print()
        print()

