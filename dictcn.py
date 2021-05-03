import requests
import sqlite3

class Dictcn():

    def save(self, word, meaning):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()
        cursor.execute("SELECT count(1) FROM dict WHERE word='{}' and source='DICTCN'".format(word))
        if cursor.fetchone()[0] != 0:
            conn.close()
            return
        cursor.execute("INSERT INTO dict (word, meaning, source) VALUES ('{}', '{}', 'DICTCN')".format(word, meaning))
        conn.commit()
        conn.close()

    def skipspace(self, str):
        result = ''
        for i in range(0, len(str)):
            if str[i] != '\n' and str[i] != '\t' and str[i] != ' ':
                result = result + str[i]
        return result

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
            result = result + self.skipspace(htmlsegment[pos+1:contentend])
            pos = htmlsegment.find('>', contentend)

        return result[2:]

    def search(self, word):
        try:
            conn = sqlite3.connect('dict.db')
            cursor = conn.cursor()

            cursor.execute("SELECT word, meaning FROM dict where word='{}' COLLATE NOCASE and source='DICTCN'".format(word))
            row = cursor.fetchone()
            if row != None:
                #print('find record word={}'.format(row[0]))
                query_word = row[0]
                query_meaning = row[1]
                conn.close()
                return '{}|{}'.format(query_word, query_meaning)

            #print('word='+word)
            url = 'https://dict.cn/search?q={}'.format(word)
            headers = {'Host': 'dict.cn',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate',
                   'Referer': 'http://www.baidu.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', }
            response = requests.get(url=url, headers=headers)
            #print(response.text)

            #wordstart = response.text.find('<h1 class="keyword"')
            #if wordstart == -1:
                #print('word {} not found, skip.'.format(word))
                #print(word)
                #return ''
            #wordend = response.text.find('</h1>', wordstart)
            #findword=response.text[response.text[wordstart:].find('>')+wordstart+1:wordend]

            wordend = response.text.find('的相关资料：<i tip="词的相关资料"')
            wordstart = response.text[:wordend].rfind('>')
            findword = response.text[wordstart+1:wordend]
            print('word={};wordstart={};wordend={};findword={}'.format(word, wordstart, wordend, findword))

            #print(findword)

            meanstart = response.text.find('<div class="basic clearfix">')
            meanend = response.text.find('<script', meanstart)

            findmean=response.text[meanstart + len('<div class="basic clearfix">'):meanend]

            #print(self.skiptrash(findmean))
            self.save(findword, self.skiptrash(findmean))
            return '{}|{}'.format(findword, self.skiptrash(findmean))

        except Exception as e:
            print(e)

    def duqudanci(self, file):
        wordcount = 0
        for line in open(file):
            word = line.strip('\n')
            wordcount += 1
            #print(wordcount)
            result = self.searchInCiba(word)

            if result == '': #如果读取失败，则再试一次
                result = self.searchInCiba(word)

            if result != '':
                with open("words/result.txt", 'a') as f:
                    f.write(result + '\n')
                    # print(result)
            else:
                print(word)
            #print('\n')

if __name__ == '__main__':
    word = "cosgrove"
    # 需要爬取的单词
    youdao = Dictcn()
    youdao.search(word)
