import pymysql
import csv
import time

class BookList():
    # 从 csv 读取出的 book item
    book_list = []
    # 将 book item 插入数据库 的 sql 语句
    sql_list = []
    # 统计本文档出现了哪些 category, 方便统一替换
    category_set = set()

    def __init__(self):
        pass

    # 从 csv 文件遍历信息
    def read_csv(self):
        # with open('aibooks_3_21_OUT.csv', 'r', encoding='ansi' ) as f:
        with open('obooks_OUT.csv', 'r') as f:
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
                    title = i[0]
                    author = i[1]
                    rating = i[2]
                    catogory = self.format_category(i[3])
                    # catogory = i[3]
                    self.category_set.add(i[3])
                    infos = i[4]
                    description = i[5]
                    pic = i[6]
                    pan_1 = i[7]
                    pan_2 = i[8]
                    pan_3 = i[9]
                    # pan_1 pan_2 pan_3 均为空值
                    l_1 = len(pan_1)
                    l_2 = len(pan_2)
                    l_3 = len(pan_3)
                    if not ( l_1 + l_2 + l_3 ):
                        continue
                    pan_pass = '百度网盘提取码:' + i[10]
                    origin = i[11]

                    # 生成 book item 字典， 并保存到 self.book_list[]
                    self.gen_book_item(title, pic, author, catogory, infos, description, origin, pan_1, pan_2, pan_3, pan_pass, rating)
                except Exception as e:
                    print(e)
                    print('读数据时遇到一个问题项，已跳过')
                    continue
                finally:
                    pass

    # 展示 本文档 所包含的 category Set
    def show_category(self):
        print('\n开始输出 self.category_set')
        for c in self.category_set:
            print(c)
        print('输出 self.category_set 完成')

    # 解决 book_category 标准不一致的情况
    # 如： 计算机科学 -> 自我提升
    def format_category(self, category):
        # 小说文学
        c_list_1 = ['中国语言文学', '小说', '网文', '国学', '名著', '古籍', '随笔', '儿童', '绘本', '散文', '文学', '原版', ]
        # 人文社科
        c_list_2 = ['社科', '知乎', '社会学', '健康', '英语', '杂志', '合集', '文化', '法律', ]
        # 励志成功
        c_list_3 = ['心理', '哲学', '成长', '励志', ]
        # 历史传记
        c_list_4 = ['纪实', '传记', '历史', ]
        # 学习教育
        c_list_5 = ['科普', '设计', '医学', '科技', '数学', '工学', '教材', '教育', ]
        # 生活时尚
        c_list_6 = ['漫画', '艺术', '旅行', '婚恋', '摄影', '生活', ]
        # 经济管理
        c_list_7 = ['商业', '经济金融', '经济学', '管理', ]
        # 编程开发
        c_list_8 = ['信息科学技术', '互联网', '编程', '计算机', ]

        if category in c_list_1:
            return '小说文学'
        elif category in c_list_2:
            return '人文社科'
        elif category in c_list_3:
            return '励志成功'
        elif category in c_list_4:
            return '历史传记'
        elif category in c_list_5:
            return '学习教育'
        elif category in c_list_6:
            return '生活时尚'
        elif category in c_list_7:
            return '经济管理'
        elif category in c_list_8:
            return '编程开发'
        else:
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
    # b_list.show_category()
    b_list.gen_sql()
    b_list.item_2_db()
    '''
    for i in b_list.sql_list:
        print(i)
        print('###')

    print('共 ' + str(len(b_list.sql_list)))
    '''

main()