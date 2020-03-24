import pymysql
import csv
import time

class BookList():
    # 从 csv 读取出的 book item
    book_list = []
    # 将 book item 插入数据库 的 sql 语句
    sql_list = []

    def __init__(self):
        pass

    # 从 csv 文件遍历信息
    def read_csv(self):
        # with open('aibooks_3_21_OUT.csv', 'r', encoding='ansi' ) as f:
        with open('pdfbook_spider/pdfbook_3.24_backup.csv', 'r') as f:
            reader = csv.reader(f)
            # 第一行是标题，不需要读
            # title_readed = True
            for i in reader:
                '''
                if title_readed:
                    title_readed = False
                    continue
                '''
                book_item = {}
                try:
                    title = i[11]
                    author = i[0]
                    rating = i[10]
                    catogory = self.format_category(i[1])
                    infos = i[3]
                    description = i[2]
                    pic = i[9]
                    pan_1 = i[5]
                    pan_2 = i[6]
                    pan_3 = i[7]
                    # pan_1 pan_2 pan_3 均为空值
                    l_1 = len(pan_1)
                    l_2 = len(pan_2)
                    l_3 = len(pan_3)
                    if not ( l_1 + l_2 + l_3 ):
                        continue
                    pan_pass = i[8]
                    origin = i[4]

                    # 生成 book item 字典， 并保存到 self.book_list[]
                    self.gen_book_item(title, pic, author, catogory, infos, description, origin, pan_1, pan_2, pan_3, pan_pass, rating)
                except Exception as e:
                    print(e)
                    print('读数据时遇到一个问题项，已跳过')
                    continue
                finally:
                    pass

    # 解决 book_category 标准不一致的情况
    # 如： 计算机科学 -> 自我提升
    def format_category(self, category):
        '''
        # 小说文学
        c_list_1 = []
        # 人文社科
        c_list_2 = []
        # 励志成功
        c_list_3 = []
        # 历史传记
        c_list_4 = []
        # 学习教育
        c_list_5 = []
        # 生活时尚
        c_list_6 = []
        # 经济管理
        c_list_7 = []
        # 编程开发
        c_list_8 = []
        # 英文原版
        c_list_9 = []
        '''
        # 统一将 book_category 改为 [其它]
        return '其它'
        

    # 由给定的信息 生成 book item 并保存到 self.book_list[]
    def gen_book_item(self, title, pic, author, catogory, infos, description, origin, pan_1, pan_2, pan_3, pan_pass, rating):
        book = {}
        book['title'] = title
        book['pic'] = pic
        book['author'] = author
        book['catogory'] = catogory
        book['infos'] = infos
        book['description'] = description
        book['origin'] = origin
        book['pan_1'] = pan_1
        book['pan_2'] = pan_2
        book['pan_3'] = pan_3
        book['pan_pass'] = pan_pass
        book['rating'] = rating

        self.book_list.append(book)

    # 生成 插入 book_item 的 sql 语句
    # 将 self.book_list[] 中的所有 book item 都转化为 sql 插入语句，并放在 self.sql_list[]
    def gen_sql(self):
        for book in self.book_list:
            sql_base = 'INSERT INTO books_books ( book_title, book_pic, book_author, book_category, book_infos, book_description, book_origin, book_pan_1, book_pan_2, book_pan_3, book_pan_pass, book_rating, book_valid, book_views, book_pub_date) VALUES ('
            sql_base += '"' + book['title'] + '", '
            sql_base += '"' + book['pic'] + '", '
            sql_base += '"' + book['author'] + '", '
            sql_base += '"' + book['catogory'] + '", '
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

            self.sql_list.append(sql_base)

    # 写入数据 至 mysql 数据库
    # 遍历 self.sql_list[] , 依次执行每一条 sql 语句
    def item_2_db(self):
        conn = pymysql.connect('127.0.0.1', port=3306, user='root', password='xqksj', db='bdpan', charset='utf8')
        cursor = conn.cursor()

        for i in self.sql_list:
            try:
                cursor.execute(i)
                conn.commit()
            except:
                conn.rollback()
        cursor.close()
        conn.close()


def main():
    b_list = BookList()
    b_list.read_csv()
    b_list.gen_sql()
    b_list.item_2_db()
    '''
    for i in b_list.sql_list:
        print(i)
        print('###')
    '''

    print('共 ' + str(len(b_list.sql_list)))

main()