import requests
from bs4 import BeautifulSoup
import time
import csv


class AiBooks_Spider():
    request_header = {
        'authority':'www.aibooks.cc',
        'method':'GET',
        # path
        'path':'/page/3',
        'scheme':'https',
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN,zh;q=0.9',
        'cache-control':'no-cache',
        'cookie':'UM_distinctid=16f55d42b94e0-0de41fcfc15d97-1d326b5b-100200-16f55d42b9523d; __51cke__=; CNZZDATA1276692267=340145870-1577691287-https%253A%252F%252Fwww.google.com%252F%7C1584717751; __tins__19961385=%7B%22sid%22%3A%201584719852924%2C%20%22vd%22%3A%2011%2C%20%22expires%22%3A%201584722118974%7D; __51laig__=22',
        'pragma':'no-cache',
        # referer
        'referer':'https://www.aibooks.cc/page/2',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    # 当前正砸爬取的 page 页
    now_page = 26
    total_pages = 7960
    # 用于拼接 目录 page URL: https://www.aibooks.cc/page/3
    base_page_url = 'http://www.52book.me/page/'
    # 图书详情页 URL 列表
    book_detail_list = []
    # 生成的 图书对象 列表
    book_item_list = []
    # 生成 csv 文件
    title_list = ['title', 'author', 'rating', 'catogory', 'infos', 'pic',
    'pan_1', 'pan_2', 'pan_3', 'pan_pass', 'origin']
    # 解析详情 出错的 page/目录页/详情页 URL 列表
    err_parse_list = []
    
    def __init__(self):
        pass

    # 解析目录
    def parse_menu(self):
        while ( self.now_page < self.total_pages ):
            # 下一页 目录 的URL
            next_page_url = self.base_page_url + str(self.now_page)
            print('开始解析第 ' + str(self.now_page) + ' 页')
            print(next_page_url)

            self.get_detail_url(next_page_url)

            self.now_page += 1

        print('\n已解析完所有 page 页\n')
        if len(self.err_parse_list):
            print('以下是解析失败的URL:')
            for e_url in self.err_parse_list:
                print(e_url)

    # 从 主页/目录 中提取图书详情页 URL
    # url: 待解析的目录页
    def get_detail_url(self, url):
        soup = BeautifulSoup( self.get_html(url), 'lxml' )
        for c in soup.select("div.recentpost_listing"):
            try:
                detail_url = c.article.div.a['href']
                catogory = c.article.div.div.a.text
                title = c.article.header.h3.a.text
                pic = c.div.a.img['data-src']
                # 解析详情页
                self.parse_detail( detail_url, catogory, title, pic )
            except Exception as e:
                print('解析目录 出错了 page:' + str(self.now_page))
                print(url)

        # 解析完 本page页 后写入数据到 csv
        self.toCsv()

    # 解析详情页的各种图书信息
    # url: 待解析的详情页
    def parse_detail(self, url, catogory, title, pic):
        # for d_url in self.get_detail_url:
        d_url = url 
        print()
        print(title)
        print('开始解析：' + d_url)

        soup = BeautifulSoup( self.get_html(d_url), 'lxml' )

        try:
            # 图书 作者 简介 等信息
            infos = soup.select("div.entry-content")[0].text

            # 图书 网盘链接
            # 需要先请求这个 URL ，302 重定向得到 城通网盘 URL
            chengtong = 'http://www.52book.me' + soup.select("div.entry-content")[0].a['href']
            pan_1 = requests.get(chengtong).url

            # 生成 书籍对象
            book_item = self.gen_book_item(title, '未知', '未知', catogory, infos, pic, pan_1,'', '', '无密码', d_url)
            self.book_item_list.append(book_item)
            time.sleep(1)
        except Exception as e:
            print('爬取出错 第 ' + str(self.now_page) + ' 页')
            self.err_parse_list.append( 'page' + str(self.now_page) + '#' + url)
            print('已加入 err_parse_list\n')

    # 生成 book对象 字典，方便调用
    def gen_book_item(self, title, author, rating, catogory, infos, pic, pan_1, pan_2, pan_3, pan_pass, origin):
        book_i = {
                'title': title,
                'author': author,
                'rating': rating,
                'catogory': catogory,
                'infos': infos,
                'pic': pic,
                'pan_1': pan_1,
                'pan_2': pan_2,
                'pan_3': pan_3,
                'pan_pass': pan_pass,
                'origin': origin,
        }

        book_i['title'] = title
        book_i['author'] = author
        book_i['rating'] = rating
        book_i['catogory'] = catogory
        book_i['infos'] = infos
        book_i['pic'] = pic
        book_i['pan_1'] = pan_1
        book_i['pan_2'] = pan_2
        book_i['pan_3'] = pan_3
        book_i['pan_pass'] = pan_pass
        book_i['origin'] = origin

        return book_i


    # 请求网络 获取 html
    # url: 待请求的 URL
    def get_html(self, url):
        try:
            r = requests.get( url, timeout = 15 )
            return r.text
        except Exception as e:
            print('get_html 出错')
            print(e)

            return 0

    # 写入数据到 csv 文件
    def toCsv(self):
        # 写入 csv 文件 ; encoding 解决用 wps 打开后中文乱码
        out_file_name = '/Users/lynn/52books_OUT.csv'
        print("OUT:" + out_file_name)
        with open(out_file_name, 'a', encoding = 'utf-8-sig') as csvfile:
            # fieldnames = self.title_list_cn
            fieldnames = self.title_list
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            #注意header是个好东西
            # writer.writeheader()
            for u_items in self.book_item_list:
                writer.writerow(u_items)
        print("All Down !! 共写入数据 " + str(len(self.book_item_list)))
        # 清空 self.book_item_list 列表, 防止重复写入
        self.book_item_list = []
        time.sleep(1)

    # 从 aibook_errlist.txt 中加载解析失败的URL
    def load_parse_err_list(self):
        with open('/Users/lynn/Desktop/好书分享君/图书采集程序/52book_errlist.txt', 'r') as f:
            for line in f.readlines():
                self.err_parse_list.append(line)
        print('load_parse_err_list 完成')
        print('共 ' + str(len(self.err_parse_list)))

        for i in self.err_parse_list:
            print(i)

        time.sleep(5)


def main():
    aibook = AiBooks_Spider()
    # aibook.load_parse_err_list()
    aibook.parse_menu()

main()