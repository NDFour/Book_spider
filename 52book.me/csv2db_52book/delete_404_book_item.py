import requests
import pymysql

def get_id_book_pan1():
    conn = pymysql.connect('127.0.0.1', port=3306, user='root', password='xqksj', db='bdpan', charset='utf8')
    cursor = conn.cursor()

    sql_id_pan = "select id,book_pan_1 from books_books;"
    # 从数据库中国查询出的 id pan_url 对
    item_list = []
    # 网盘链接已失效的 id 列表
    invalid_id_list = []
    try:
        cursor.execute(sql_id_pan)
        conn.commit()

        for url in cursor.fetchall():
        	item_list.append( {'id': url[0], 'pan': url[1]} )
        print('查询数据库完成')

        for item in item_list:
        	if is_valid(item['pan']):
        		pass
        	else:
        		invalid_id_list.append(item['id'][6:])
        print('所有 pan_url 已检测完毕')
        print('开始执行删除操作')

        delete_item(invalid_id_list)

    except:
        conn.rollback()
    finally:
	    cursor.close()
	    conn.close()

	pritn('程序运行结束')


# 链接数据库，根据 id 删除 pan_url 已失效的数据
def delete_item(invalid_id_list):
    conn = pymysql.connect('127.0.0.1', port=3306, user='root', password='xqksj', db='bdpan', charset='utf8')
    cursor = conn.cursor()

	for i_id in invalid_id_list:
		sql_del = 'delete from books_books where id=' + i_id + ';'

	    try:
	        cursor.execute(sql_del)
	        conn.commit()
	    except:
	        conn.rollback()

    cursor.close()
    conn.close()

def is_valid(url):
	print('开始检测 pan_url 是否有效')
	pass


def main():
	get_id_book_pan1()

main()