import requests
from bs4 import BeautifulSoup
import time
import csv

import pymysql

import smtplib
from email.mime.text import MIMEText


class AiBooks_Spider():

    request_header = {
        'authority': 'www.aibooks.cc', 
        'method': 'GET',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    }


    # 图书详情页 URL 列表
    book_detail_list = []
    # 生成的 图书对象 列表
    book_item_list = []
    # 生成 csv 文件
    title_list = ['title', 'author', 'rating', 'category', 'infos', 'pic',
    'pan_1', 'pan_2', 'pan_3', 'pan_pass', 'origin']


    def __init__(self):
        print('## AiBooks_Spider init...')

    # 用于 chenjin5.com 图书自动更新
    def auto_update(self):
        index_page = 'https://www.aibooks.cc'
        self.get_detail_url(index_page)


    # 从 主页/目录 中提取图书详情页 URL
    # url: 待解析的目录页
    def get_detail_url(self, url):
        soup = BeautifulSoup( self.get_html(url), 'lxml' )
        book_cnt = 0
        for c in soup.select("div.card-item"):
            # 先判断该图书是否已存在数据库中
            print(c.h3.a['href'])
            if is_crawled(c.h3.a['href']):
                print('^ 已爬取过')
                print()
                continue
            else:
                print('^ 未爬取过')
                print()
            # self.book_detail_list.append( c.h3.a['href'] )
            # 分类
            category = self.convert_category( c.div.div.a.text.strip() )
            # 作者
            author = c.p.text[3:].strip()
            # 豆瓣评分
            rating = c.font.text.strip()
            # 解析详情页
            self.parse_detail( c.h3.a['href'], author, rating, category )
            book_cnt += 1


    # 将从本网站提取到的 category 转换成 chenjin5 专用
    def convert_category(self, category):
        category_dic = {
            '小说文学': '小说文学',
            '人文社科': '人文社科',
            '励志成功': '励志成功',
            '历史传记': '历史传记',
            '学习教育': '学习教育',
            '生活时尚': '生活时尚',
            '经济管理': '经济管理',
            '编程开发': '编程开发',
            '英文原版': '其它',
        }

        try:
            rel = category_dic[category]
        except Exception as e:
            rel = '其它'

        # print('-> convert_category:' + category + ' -> ' + rel)

        return rel


    # 解析详情页的各种图书信息
    # url: 待解析的详情页
    def parse_detail(self, url, author, rating, category):
        # for d_url in self.get_detail_url:
        d_url = url 
        # print()
        # print('开始解析：' + d_url)

        soup = BeautifulSoup( self.get_html(d_url), 'lxml' )
        # 标题部分 主要有书名等信息
        soup_header = soup.select("header.article-header")[0]

        try:
            title = soup_header.h1.text
            # print(title)

            try:
                description = soup.article.p.text.strip()
            except Exception as e2:
                description = '暂无'

            # 图书 作者 简介 等信息
            infos = ''

            for info in soup_header.ul.select("li"):
                infos += info.text
                infos += "*-*"
            # 图书封面
            pics = soup_header.img['src']
            # 图书 网盘链接
            pan_cnt = 0
            pan_1 = ''
            pan_2 = ''
            pan_3 = ''
            for pan in soup.table.select("a"):
                if pan_cnt == 0:
                    pan_1 = pan.text + '##' + pan['href']
                elif pan_cnt == 1:
                    pan_2 = pan.text + '##' + pan['href']
                elif pan_cnt == 2:
                    pan_3 = pan.text + '##' + pan['href']
                pan_cnt += 1
            # 图书 网盘 提取码
            pan_pass = soup.select("div.alert")[0].text

            # 生成 书籍对象
            book_item = self.gen_book_item(title, author, rating, category, infos, description, pics, pan_1, pan_2, pan_3, pan_pass, url)
            self.book_item_list.append(book_item)
            time.sleep(1)
        except Exception as e:
            print(e)

    # 生成 book对象 字典，方便调用
    def gen_book_item(self, title, author, rating, category, infos, description, pic, pan_1, pan_2, pan_3, pan_pass, origin):
        book_i = {
                'title': title,
                'author': author,
                'rating': rating,
                'category': category,
                'infos': infos,
                'description': description,
                'pic': pic,
                'pan_1': pan_1,
                'pan_2': pan_2,
                'pan_3': pan_3,
                'pan_pass': pan_pass,
                'origin': origin,
        }

        return book_i


    # 请求网络 获取 html
    # url: 待请求的 URL
    def get_html(self, url):
        try:
            r = requests.get( url, timeout = 30 )
            return r.text
        except Exception as e:
            print('get_html 出错')
            print(e)

            return 0

    # 展示已爬取到的 book_item
    def show_book_item(self):
        for book in self.book_item_list:
            print(book)
            print()



# 判断该图书是否已存在于数据库中
def is_crawled(origin_url):
    conn = pymysql.connect('127.0.0.1', port=3306, user='root', password='xqksj', db='bdpan', charset='utf8')
    cursor = conn.cursor()

    sql_cmd = 'select id from books_books where book_origin="' + origin_url + '";'

    rel_cnt = cursor.execute(sql_cmd)
    if rel_cnt:
        return True
    else:
        return False


# 将爬取到的数据存储到数据库
def save_2_db( sql_list ):
    conn = pymysql.connect('127.0.0.1', port=3306, user='root', password='xqksj', db='bdpan', charset='utf8')
    cursor = conn.cursor()

    succ_cnt = 0
    fail_cnt = 0
    for i in sql_list:
        try:
            cursor.execute(i)
            conn.commit()
            succ_cnt += 1
        except:
            conn.rollback()
            fail_cnt += 1
    cursor.close()
    conn.close()

    print('succ_cnt:' + str(succ_cnt))
    print('fail_cnt:' + str(fail_cnt))


# 生成 插入 book_item 的 sql 语句
# 将 self.book_list[] 中的所有 book item 都转化为 sql 插入语句，并放在 self.sql_list[]
def gen_sql( book_list ):
    sql_list = []
    for book in book_list:
        sql_base = 'INSERT INTO books_books ( book_title, book_pic, book_author, book_category, book_infos, book_description, book_origin, book_pan_1, book_pan_2, book_pan_3, book_pan_pass, book_rating, book_valid, book_views, book_pub_date) VALUES ('
        sql_base += '"' + book['title'] + '", '
        sql_base += '"' + book['pic'] + '", '
        sql_base += '"' + book['author'] + '", '
        sql_base += '"' + book['category'] + '", '
        sql_base += '"' + book['infos'] + '", '
        sql_base += '"' + book['description'] + '", '
        sql_base += '"' + book['origin'] + '", '
        sql_base += '"' + book['pan_1'] + '", '
        sql_base += '"' + book['pan_2'] + '", '
        sql_base += '"' + book['pan_3'] + '", '
        sql_base += '"' + book['pan_pass'] + '", '
        sql_base += '"' + book['rating'] + '", '
        sql_base += '1, '
        sql_base += '0, '
        sql_base += '"' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime() ) + '");'

        sql_list.append(sql_base)

    return sql_list


# 推送消息到邮箱
def mailtestmsg(book_item_list):
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 发邮件代码
    _user = "lgang219@qq.com"
    _pwd  = "xxxxxxxxxxxxx"
    _to   = "ndfour@foxmail.com"

    mail_content = '今日更新:\n\n'
    if len(book_item_list):
        try:
            for book in book_item_list:
                mail_content += book['title']
                mail_content += '\n'
                mail_content += book['category']
                mail_content += '\n'
                mail_content += book['origin']
                mail_content += '\n\n'
        except Exception as e:
            pass
    else:
        mail_content += '今日没有新内容'
    msg = MIMEText( mail_content )
    msg["Subject"] = "[chenjin5 Auto Update] 日更提醒邮件"
    msg["From"] = _user
    msg["To"] = _to

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(_user, _pwd)
        s.sendmail(_user, _to, msg.as_string())
        s.quit()
    except Exception as e:
        pass




# 上传前移除发邮件密码
# 上传前移除发邮件密码
# 上传前移除发邮件密码

def main():
    # aibook
    aibook = AiBooks_Spider()
    aibook.auto_update()
    # aibook.show_book_item()
    sql_list = gen_sql(aibook.book_item_list)
    save_2_db(sql_list)

    mailtestmsg(aibook.book_item_list)


main()