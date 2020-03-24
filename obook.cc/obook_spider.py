import requests
from bs4 import BeautifulSoup
import time
import csv


class OBooks_Spider():
    request_header = {
    }

    # request 下的 session 用于 模拟登陆
    obook_session = requests.Session()
    # 当前正砸爬取的 page 页
    now_page = 1
    # total_pages = 483
    total_pages = 3
    # 用于拼接 目录 page URL: https://www.obook.cc/index-50.htm
    base_page_url = 'https://www.obook.cc/index-'
    # 图书详情页 URL 列表
    book_detail_list = []
    # 生成的 图书对象 列表
    book_item_list = []
    # 生成 csv 文件
    title_list = ['title', 'author', 'rating', 'category', 'infos', 'description', 'pic',
    'pan_1', 'pan_2', 'pan_3', 'pan_pass', 'origin']
    # 解析详情 出错的 page/目录页/详情页 URL 列表
    err_parse_list = []
    
    def __init__(self):
        pass

    # 模拟登陆
    def login(self):
        login_url = 'https://www.obook.cc/user-login.htm'
        form_data = {
            'email': 'seend',
            'password': 'aa4d74090a61febb3465c13966148a86',
        }
        self.obook_session.post(login_url, data = form_data, timeout = 30)
        print('登陆完成，尝试抓取数据')

    # 模拟推出
    def logout(self):
        logout_url = 'https://www.obook.cc/user-logout.htm'
        self.obook_session.get(logout_url, timeout = 30)
        print('\n\n模拟推出 完成')

    # 解析目录
    def parse_menu(self):
        while ( self.now_page < self.total_pages ):
            # 下一页 目录 的URL
            next_page_url = self.base_page_url + str(self.now_page) + '.htm'
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
        for c in soup.select("div.card-body")[0].ul.select("li"):
            # self.book_detail_list.append( c.h3.a['href'] )
            # 分类
            try:
                category = c.div.select("div")[1].div.a.text
            except Exception as e:
                print('从 menu_url 获取 category 失败')
                print(e)
            # 作者
            author = '请参考图书详情'
            # 豆瓣评分
            rating = ''
            # 解析详情页
            try:
                href = 'https://www.obook.cc/' + c.a['href']
                self.parse_detail( href, author, rating, category )
            except Exception as e:
                print('从 menu_url 解析 href 失败, 跳过')
                print(e)
        # 解析完 本page页 后写入数据到 csv
        self.toCsv()

    # 解析详情页的各种图书信息
    # url: 待解析的详情页
    def parse_detail(self, url, author, rating, category):
        # for d_url in self.get_detail_url:
        d_url = url 
        print()
        print('开始解析：' + d_url)

        soup = BeautifulSoup( self.get_html(d_url), 'lxml' )
        book_content = soup.select("div.card-thread")[0].div

        title = self.extract_title(book_content)
        if not title:
            self.err_parse_list.append(url)
            print('已将 url 加入 self.err_parse_list[]')
            return

        # 图书 作者 简介 等信息
        infos = self.extract_infos(book_content)

        # 内容简介
        description = self.extract_description(book_content)

        # 图书封面
        pic = self.extract_pic(book_content)

        # 图书 网盘链接
        pan_1 = self.extract_pan_1(book_content)
        pan_2 = self.extract_pan_2(book_content)
        pan_3 = self.extract_pan_3(book_content)
        len_pan = len(pan_1) + len(pan_2) + len(pan_3)
        if not len_pan:
            self.err_parse_list.append(url)
            print('一个网盘链接都没有找到，已将 URL 加入 self.err_parse_list[]')
            return

        # 图书 网盘 提取码
        pan_pass = self.extract_pan_pass(book_content)

        # 生成 书籍对象
        book_item = self.gen_book_item(title, author, rating, category, infos, pic, pan_1, pan_2, pan_3, pan_pass, url)
        self.book_item_list.append(book_item)


    # 从详情页 提取 title
    def extract_title(self, book_content):
        title = ''
        try:
            title = book_content.div.div.h4.text.strip()
            print(title)
        except Exception as e:
            print('爬取 title 失败')
            print(e)
        return title

    # 从详情页 提取 infos
    def extract_infos(self, book_content):
        return ''

    # 从详情页 提取 description
    def extract_description(self, book_content):
        description = ''
        try:
            description = book_content.select("div#hide-line")[0].text
        except Exception as e:
            print('爬取 description 失败')
            print(e)
            print('########### description')
        return description

    # 从详情页 提取 pic
    def extract_pic(self, book_content):
        pic = ''
        try:
            pic = book_content.select("div.message")[0].img['src']
        except Exception as e:
            print('爬取 pic 失败')
            print(e)
            print('########### pic')
        return pic

    # 从详情页 提取 pan_1
    def extract_pan_1(self, book_content):
        pan_1 = ''
        try:
            pan_1 = '百度网盘##' + book_content.table.a['href']
        except Exception as e:
            print('爬取网盘链接失败')
            print(e)
            print('########### pan_1')
        return pan_1

    # 从详情页 提取 pan_2
    def extract_pan_2(self, book_content):
        return ''

    # 从详情页 提取 pan_3
    def extract_pan_3(self, book_content):
        return ''

    # 从详情页 提取 pan_pass
    def extract_pan_pass(self, book_content):
        pan_pass = ''
        try:
            pan_pass = book_content.table.select("td")[2].input['value']
        except Exception as e:
            print('爬取网盘提取码失败')
            print(e)
            print('########### pan_pass')
        return pan_pass


    # 生成 book对象 字典，方便调用
    def gen_book_item(self, title, author, rating, category, infos, pic, pan_1, pan_2, pan_3, pan_pass, origin):
        book_i = {
                'title': title,
                'author': author,
                'rating': rating,
                'category': category,
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
        book_i['category'] = category
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
        time.sleep(1)
        try:
            r = self.obook_session.get( url, timeout = 30 )
            return r.text
        except Exception as e:
            print('get_html 出错')
            print(e)

            return ''

    # 写入数据到 csv 文件
    def toCsv(self):
        # 写入 csv 文件 ; encoding 解决用 wps 打开后中文乱码
        out_file_name = '/Users/lynn/Desktop/好书分享君/图书采集程序/obook.cc/obooks_OUT.csv'
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


    # 发送微信消息提醒
    def wechat_notify(self, status):
        # Server 酱 / 微信提醒 URL
        wechat_url = 'https://sc.ftqq.com/SCU52512T77e075b86690b62f884c8eeec4d6969f5cef37ed7855c.send'
        # Server 酱 消息题
        notify_data = {
            'text':'我是标题',
            'desp':'我是内容',
        }


        if status == 1:
            notify_data['text'] = 'obook.cc_spider 开始运行'
            notify_data['desp'] = '开始运行 ' + time.ctime()
        elif status == 0:
            notify_data['text'] = 'obook.cc_spider 结束运行'
            notify_data['desp'] = '结束运行 ' + time.ctime()

        r = requests.get( wechat_url, params = notify_data, timeout = 10 )


def main():
    obook = OBooks_Spider()
    obook.wechat_notify(1)
    obook.login()
    obook.parse_menu()
    obook.logout()
    obook.wechat_notify(0)

main()