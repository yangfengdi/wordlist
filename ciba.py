import requests

class Ciba():

    def skiptrash(self, htmlsegment):
        result = ''
        pos = 0
        #print(htmlsegment)
        while True:
            contentend = htmlsegment.find('<', pos)
            if contentend == -1:
                break
            #print('pos={} contentend={}'.format(pos+1, contentend))
            #print(htmlsegment[pos+1:contentend])
            if htmlsegment[pos+1:].startswith('大小写变形'):
                break
            if htmlsegment[pos+1-4:pos+1]=='<li>':
                result = result + '; '
            result = result + htmlsegment[pos+1:contentend]
            pos = htmlsegment.find('>', contentend)

        return result[2:]

    def search(self, word):
        try:
            #print('word='+word)
            #url = "https://www.iciba.com/word?w={}".format(word)
            url = 'https://dict.iciba.com/dictionary/word/query/web?word={}'.format(word)
            #headers = {'Host': 'www.iciba.com',
            #       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            #       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            #       'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate',
            #       'Referer': 'http://www.baidu.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', }
            headers = {'Host': 'www.iciba.com',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate',
                   'Referer': 'http://www.baidu.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', }
            #print('start request')
            response = requests.get(url=url, headers=headers)
            #print('request finished')

            if response.status_code != 200:
                print('金山词霸网站服务器异常，status_code={}, word={}'.format(response.status_code, word))

            wordstart = response.text.find('<h1 class="Mean_word__3SsvB">')
            if wordstart == -1:
                #print('word {} not found, skip.'.format(word))
                #print(word)
                return ''
            wordend = response.text.find('<img', wordstart)
            findword=response.text[wordstart + len('<h1 class="Mean_word__3SsvB">'):wordend]

            #print(findword)

            meanstart = response.text.find('<ul class="Mean_part__1RA2V">')
            meanend = response.text.find('<div class="FoldBox_fold__1GZ_2">', meanstart)
            if meanend == -1:
                meanend = response.text.find('京ICP备', meanstart)

            findmean=response.text[meanstart + len('<ul class="Mean_part__1RA2V">'):meanend]

            #print(skiptrash(findmean))

            return '{}|{}'.format(findword, self.skiptrash(findmean))

        except Exception as e:
            print(e)

    def duqudanci(self, file):
        wordcount = 0
        for line in open(file):
            word = line.strip('\n')
            wordcount += 1
            #print(wordcount)
            result = self.search(word)

            if result == '': #如果读取失败，则再试一次
                result = self.search(word)

            if result != '':
                with open("words/result.txt", 'a') as f:
                    f.write(result + '\n')
                    # print(result)
            else:
                print(word)
            #print('\n')

if __name__ == '__main__':
    word = ""
    # 需要爬取的单词
    ciba = Ciba()
    ciba.duqudanci('words/words.txt')
    print('下载完成！请到words/result.txt文件中读取结果。\n下载失败的单词已经在上方打印出来，请注意核对并考虑重试。')
