import pymysql
import csv
import time

class BookList():
    # 从 csv 读取出的 book item
    book_list = []
    # 将 book item 插入数据库 的 sql 语句
    sql_list = []

    # 补全 pic
    # 存放 修改 pic 后的 book_item
    new_item_list = []
    href_pic_list = []

    def __init__(self):
        pass

    # 从 href_pic.csv 读取信息
    def read_csv_from_hrefpic(self):
        # with open('aibooks_3_21_OUT.csv', 'r', encoding='ansi' ) as f:
        with open('52book_3.23_href_pic.csv', 'r') as f:
            reader = csv.reader(f)
            # 第一行是标题，不需要读
            for i in reader:
                try:
                    href = i[0].strip()
                    pic = i[1]
                    # 生成 book item 字典， 并保存到 self.href_pic_list[]
                    self.href_pic_list.append({'href': href, 'pic': pic})
                except Exception as e:
                    print(e)
                    print('读数据时遇到一个问题项，已跳过')
                    continue
                finally:
                    pass

    # 将 href_pic_list[] 中的 pic 信息 补全到 book_list[]
    def acomplish_pic(self):
        # 已进行过匹配的
        item_cnt = 0
        # 已匹配成功的
        item_cnt_succ = 0
        for pic in self.href_pic_list:
            '''
            if item_cnt > 50:
                print('已测试 50 个 ， 退出')
                return
            '''
            print( str(item_cnt) + ' / ' + str(len(self.href_pic_list)) )
            href = pic['href']
            item = self.get_item_from_book_list(href)
            if item:
                item['pic'] = pic['pic']
                self.new_item_list.append(item)
                item_cnt_succ += 1
            else:
                pass
            item_cnt += 1
        # 将 new_item_list[] 指向 book_list[]
        self.book_list = self.new_item_list
        print('已更新 self.book_list')
        print('成功补全 ' + str(item_cnt_succ))

    # 从 book_list[] 中 找到 href == 给定参数 的 book_item
    def get_item_from_book_list(self, href):
        for i in self.book_list:
            if i['origin'] == href:
                print('找到匹配的 book_item')
                return i
        # 遍历完都未找到的话 直接 返回 None
        print('####################')
        print('未找到匹配的 book_item')
        print(href)
        print('####################')
        return None

    # 从 csv 文件遍历信息
    def read_csv(self):
        # with open('aibooks_3_21_OUT.csv', 'r', encoding='ansi' ) as f:
        with open('52book_3.23_OUT.csv', 'r') as f:
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
                    title = i[7]
                    author = i[1]
                    rating = i[2]
                    catogory = i[0]
                    infos = i[4].strip()
                    description = '暂无内容简介'
                    pic = i[3]
                    pan_1 = i[8]
                    pan_2 = i[6]
                    pan_3 = i[10]
                    pan_pass = i[5]
                    origin = i[9].strip()

                    # 生成 book item 字典， 并保存到 self.book_list[]
                    self.gen_book_item(title, pic, author, catogory, infos, description, origin, pan_1, pan_2, pan_3, pan_pass, rating)
                except Exception as e:
                    print(e)
                    print('读数据时遇到一个问题项，已跳过')
                    continue
                finally:
                    pass

    # 写入数据到 csv 文件
    def toCsv(self):
        title_list = ['catogory', 'author', 'rating', 'pic', 'infos', 'pan_pass', 'pan_2', 'title', 'pan_1', 'origin', 'pan_3', 'description']
        # 写入 csv 文件 ; encoding 解决用 wps 打开后中文乱码
        out_file_name = 'new_file.csv'
        print("OUT:" + out_file_name)
        with open(out_file_name, 'a', encoding = 'utf-8-sig') as csvfile:
            # fieldnames = self.title_list_cn
            fieldnames = title_list
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            #注意header是个好东西
            # writer.writeheader()
            for u_items in self.book_list:
                writer.writerow(u_items)

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
    '''
    b_list.gen_sql()
    b_list.item_2_db()
    '''

    # 补全 csv 中的 book_item['pic']
    b_list.read_csv_from_hrefpic()
    b_list.acomplish_pic()
    b_list.toCsv()
    # b_list.gen_sql()
    # b_list.item_2_db()
    

    '''
    for b in b_list.sql_list:
        print(b)
        print()
    '''

    print('book_list[] 共 ' + str(len(b_list.book_list)))

main()