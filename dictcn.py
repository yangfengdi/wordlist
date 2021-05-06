import requests
import sqlite3

class dict_cn():

    def save_word(self, word, meaning):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()
        sql = "SELECT count(1) FROM dict WHERE word=? and source='DICTCN'"
        cursor.execute(sql, (word, ))
        if cursor.fetchone()[0] != 0:
            conn.close()
            return
        sql = "INSERT INTO dict (word, meaning, source) VALUES (?, ?, 'DICTCN')"
        cursor.execute(sql,(word, meaning,))
        conn.commit()
        conn.close()

    def save_word_mapping(self, word, target_word, source):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()
        sql = "SELECT count(1) FROM word_mapping WHERE word=? and source='DICTCN'"
        cursor.execute(sql,(word,))

        if cursor.fetchone()[0] != 0:
            conn.close()
            return

        sql = "INSERT INTO word_mapping (word, target_word, source) VALUES (?, ?, 'DICTCN')"
        cursor.execute(sql, (word, target_word,))
        conn.commit()
        conn.close()

    def save_word_tag(self, word, tag):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "SELECT count(1) FROM word_tag WHERE word=? and tag=?"
        cursor.execute(sql, (word, tag,))
        if cursor.fetchone()[0] != 0:
            return

        sql = "INSERT INTO word_tag (word, tag) VALUES (?, ?)"
        cursor.execute(sql, (word, tag, ))
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

    def tag_word(self, word, meaning):
        if len(word) > 0:
            if word[0] in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
                self.save_word_tag(word, '首字母大写')

        if meaning.find('第三人称单数') != -1:
            self.save_word_tag(word, '第三人称单数')

        if meaning.find('复数') != -1:
            self.save_word_tag(word, '复数')

        if meaning.find('过去式') != -1:
            self.save_word_tag(word, '过去式')

        if meaning.find('过去分词') != -1:
            self.save_word_tag(word, '过去分词')

        if meaning.find('现在分词') != -1:
            self.save_word_tag(word, '现在分词')

        if meaning.find('姓氏') != -1:
            self.save_word_tag(word, '姓氏')

        if meaning.find('人名') != -1 or meaning.find('男子名') != -1 or meaning.find('女子名') != -1:
            self.save_word_tag(word, '人名')

        if meaning.find('比较级') != -1:
            self.save_word_tag(word, '比较级')

        if meaning.find('最高级') != -1:
            self.save_word_tag(word, '最高级')

        if meaning.find('国名') != -1:
            self.save_word_tag(word, '国名')

        if meaning.find('美国州名') != -1:
            self.save_word_tag(word, '美国州名')

        if meaning.find('城市') != -1:
            self.save_word_tag(word, '城市')

        if meaning.find('abbr.') != -1:
            self.save_word_tag(word, '缩写')

    def search(self, word):
        try:
            conn = sqlite3.connect('dict.db')
            cursor = conn.cursor()

            sql = "SELECT target_word FROM word_mapping where word=? and source='DICTCN'"
            cursor.execute(sql, (word,))
            row = cursor.fetchone()
            if row != None:
                word = row[0]

            if len(word) == 0:
                conn.close()
                return '', ''

            sql = "SELECT word, meaning FROM dict where word=? and source='DICTCN'"
            cursor.execute(sql, (word,))
            row = cursor.fetchone()
            if row != None:
                #print('find record word={}'.format(row[0]))
                query_word = row[0]
                query_meaning = row[1]
                conn.close()
                return query_word, query_meaning

            #print('word='+word)
            url = 'https://dict.cn/search?q={}'.format(word)
            headers = {'Host': 'dict.cn',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate',
                   'Referer': 'http://www.baidu.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', }
            response = requests.get(url=url, headers=headers)
            #print(response.text)

            wordend = response.text.find('的相关资料：<i tip="词的相关资料"')
            wordstart = response.text[:wordend].rfind('>')
            findword = response.text[wordstart+1:wordend]
            #print('word={};wordstart={};wordend={};findword={}'.format(word, wordstart, wordend, findword))

            #print(findword)
            if word != findword:
                self.save_word_mapping(word, findword, 'DICTCN')

            meanstart = response.text.find('<div class="basic clearfix">')
            meanend = response.text.find('<script', meanstart)

            findmean=response.text[meanstart + len('<div class="basic clearfix">'):meanend]

            #print(self.skiptrash(findmean))
            self.save_word(findword, self.skiptrash(findmean))

            meaning = self.skiptrash(findmean)
            self.tag_word(findword, meaning)

            return findword, meaning

        except Exception as e:
            print(e)

        return '', ''

if __name__ == '__main__':
    word = "cosgrove"
    # 需要爬取的单词
    youdao = dict_cn()
    youdao.search(word)
