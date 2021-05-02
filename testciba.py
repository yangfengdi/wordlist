# ！/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import requests

if __name__ == '__main__':
    while True:  # 无限循环
        content = input("请输入您要翻译的内容(输入 !!! 退出程序): ")
        # 设置退出条件
        if content == '!!!':
            break

        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'  # 选择要爬取的网页，上面找过了
        # 手动替换一下
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}

        # 伪装计算机提交翻译申请（下面的内容也在在上面有过，最好根据自己的进行修改）
        data = {}
        data['type'] = 'AUTO'
        data['i'] = content
        data['doctype'] = 'json'
        data['version'] = '2.1'
        data['keyfrom:'] = 'fanyi.web'
        data['ue'] = 'UTF-8'
        data['typoResult'] = 'true'
        # post请求
        response = requests.post(url, headers=header, data=data)
        # 解码
        html = response.content.decode('utf-8')
        print(html)
        # 转换为字典
        paper = json.loads(html)

        # 打印翻译结果
        print("翻译结果: %s" % (paper['translateResult'][0][0]['tgt']))
