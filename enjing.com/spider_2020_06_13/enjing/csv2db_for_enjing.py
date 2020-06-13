import pymysql
import csv
import time

class BookList():
    # 从 csv 读取出的 book item
    book_list = []
    # 将 book item 插入数据库 的 sql 语句
    sql_list = []

    category_set = set()

    def __init__(self):
        pass

    # 从 csv 文件遍历信息
    def read_csv(self):
        # with open('aibooks_3_21_OUT.csv', 'r', encoding='ansi' ) as f:
        with open('enjing/enjing.csv', 'r') as f:
            reader = csv.reader(f)
            # 第一行是标题，不需要读
            title_readed = True
            for i in reader:
                if title_readed:
                    title_readed = False
                    continue

                book_item = {}
                try:
                    title = i[11]
                    author = i[0]
                    rating = i[10]
                    catogory = self.format_category(i[1])
                    infos = i[3].strip()
                    description = i[2].strip()
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
        self.category_set.add(category)

        category_dic = {
            '中国': '人文社科',
            '青春校园':'生活时尚',
            '营销':'经济管理',
            '外国文学':'小说文学',
            '计算机':'编程开发',
            '家居':'生活时尚',
            '心灵鸡汤':'励志成功',
            '烹饪美食':'生活时尚',
            '人物传记':'历史传记',
            '法律':'学习教育',
            '侦探/悬疑/推理':'小说文学',
            '传统文学':'小说文学',
            '刑事侦查学':'人文社科',
            '中国古典文学':'小说文学',
            '诗词歌赋':'小说文学',
            '武侠仙侠':'其它',
            '玄幻奇幻':'其它',
            '散文随笔':'小说文学',
            '动漫':'小说文学',
            '国学古籍':'小说文学',
            '社交':'生活时尚',
            '当代名家作品':'小说文学',
            '古装言情':'其它',
            '现代言情':'其它',
            '历史':'历史传记',
            '英文原版':'学习教育',
            '医学':'学习教育',
            '生活百科':'生活时尚',
            '政治军事':'历史传记',
            '恐怖/惊悚':'小说文学',
            '人文社科':'人文社科',
            '科幻':'小说文学',
            '旅游':'人文社科',
            '励志成功':'励志成功',
            '金融投资':'经济管理',
            '社会官场':'人文社科',
            '经济综合':'经济管理',
            '社会科学':'人文社科',
            '励志':'励志成功',
            '管理':'经济管理',
            '文化研究':'小说文学',
            '绘画书法摄影':'学习教育',
            '哲学宗教':'人文社科',
            '心理学':'学习教育',
            '世界名著':'小说文学',
            '体育运动':'生活时尚',
            '演讲口才':'生活时尚',
            '科学技术':'学习教育',
            '经济':'经济管理',
            '建筑规划':'学习教育',
            '网络文学':'小说文学',
            '中国当代文学':'小说文学',
        }

        try:
            rel = category_dic[category]
        except Exception as e:
            rel = '其它'

        # print('-> convert_category:' + category + ' -> ' + rel)

        return rel
        

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

    with open('category.txt', 'w') as f:
        for c in b_list.category_set:
            f.write(c)
            f.write('\n')

    print('共 ' + str(len(b_list.sql_list)))

main()