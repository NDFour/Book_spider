import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import csv
import time

def read_csv(csv_name):
    contact_list = []
    try:
        # with open( csv_name, 'r', encoding = 'utf-8-sig' ) as f:
        with open( csv_name, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                contact_item = {}
                '''
                print(type(line))
                print(line)
                print()
                '''
                if line:
                    if len(line[7]):
                        contact_item['book_name'] = line[0].strip()
                        contact_item['author'] = line[1]
                        contact_item['contact_method'] = line[2]
                        contact_item['other_info'] = line[3]
                        contact_item['type'] = line[4]
                        contact_item['time'] = line[5]
                        contact_item['url'] = line[6]

                        contact_item['email'] = line[7].strip()
                        contact_item['updated_url'] = line[8].strip()
                        contact_list.append(contact_item)

    except Exception as e:
        print('read_csv failed')
        print(e)
        return

    return contact_list



# 推送消息到邮箱
def mailtestmsg(book_item):
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 发邮件代码
    _user = "lgang219@qq.com"
    _pwd  = "xxxxxxxxxx"
    # _to   = "ndfour@foxmail.com"
    _to   = book_item['email']

    mail_content = '你好，你报告的网盘链接失效图书:\n\n'
    mail_content += '《' + book['book_name'] + '》\n'
    mail_content += '网盘链接已更新：\n'
    mail_content += book['updated_url']
    mail_content += '\n\n'
    mail_content += '——————— 分割线 —————————\n'
    mail_content += "注意：由于浏览器缓存等原因，你需要等待 20 分钟左右才可以看到更新后的网盘链接。ヽ(^0^)ノ"

    print('\n----------- 开始 ----@@@@@@@@@----------------')
    print(_to)
    print('################')
    print(mail_content)
    print('----------- 结束 ----@@@@@@@@@----------------\n')

    msg = MIMEText( mail_content )
    msg["Subject"] = "八百里加急 回复 ——— 沉金书屋"
    msg["From"] = _user
    msg["To"] = _to

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(_user, _pwd)
        s.sendmail(_user, _to, msg.as_string())
        s.quit()
        print('-> 发送给 ' + book_item['email'] + ' 的邮件发送成功！')
    except Exception as e:
        print('-> 发送失败')
        print(e)


if __name__ == '__main__':
    csv_name = 'test.csv'
    contact_list = read_csv( csv_name )

    print(len(contact_list))
    for i in contact_list:
        print(i['book_name'])
        print(i['email'])
        print(i['updated_url'])
        print()
    print('###################\n')

    input('按下回车 开始发送邮件...')
    for book in contact_list:
        print('-> 准备发送给:' + book['email'])
        mailtestmsg(book)
        print()

    print()
    print('结束')