import os
import requests


# Server 酱 / 微信提醒 URL
wechat_url = 'https://sc.ftqq.com/****.send'
# Server 酱 消息题
notify_data = {
    'text':'我是标题',
    'desp':'我是内容',
}

# 发送微信消息提醒
def wechat_notify():
    r = requests.get( wechat_url, params = notify_data, timeout = 10 )

if __name__ == '__main__':
	notify_data['text'] = '52_spider 开始运行'
	notify_data['desp'] = '开始运行'
	wechat_notify()

	os.system("scrapy crawl 52book -o 2020-3-21_page1_2.csv")

	notify_data['text'] = '52_spider 结束运行'
	notify_data['desp'] = '结束运行'
	wechat_notify()
