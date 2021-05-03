import sqlite3

class dbutils():

    def import_dict(self, file, source):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        skip_count = 0
        for line in open(file):
            word = line[:line.find("|")]
            meaning = line[line.find("|") + 1:]
            meaning = meaning.strip(' ')
            meaning = meaning.strip('\n')
            meaning = meaning.strip('\r')
            meaning = meaning.strip('\t')

            if len(word) == 0 or len(meaning) == 0:
                continue

            cursor.execute("SELECT count(1) FROM dict WHERE word='{}' and source='{}'".format(word, source))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated word {}.'.format(word))
                continue

            cursor.execute("INSERT INTO dict (word, meaning, source) VALUES ('{}', '{}', '{}')".format(word, meaning, source))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} words, skip {} duplicated words.'.format(file, count, skip_count))

    def import_word_tag(self, file, tag):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        skip_count = 0
        for line in open(file):
            word = line[:line.find("|")]
            word = word.strip(' ')
            word = word.strip('\n')
            word = word.strip('\r')
            word = word.strip('\t')

            if len(word) == 0 :
                continue

            cursor.execute("SELECT count(1) FROM word_tag WHERE word='{}' and tag='{}'".format(word, tag))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated tag, word={} tag={}.'.format(word, tag))
                continue

            cursor.execute("INSERT INTO word_tag (word, tag) VALUES ('{}', '{}')".format(word, tag))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} word tags, skip {} duplicated tags.'.format(file, count, skip_count))

    def import_remember_event(self, file, remember_date):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        skip_count = 0
        for line in open(file):
            word = line[:line.find("|")]
            word = word.strip(' ')
            word = word.strip('\n')
            word = word.strip('\r')
            word = word.strip('\t')

            if len(word) == 0 :
                continue

            cursor.execute("SELECT count(1) FROM remember_event WHERE word='{}' and remember_date=strftime('%Y-%m-%d', '{}')".format(word, remember_date))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated remember event, word={} remember_date={}.'.format(word, remember_date))
                continue

            cursor.execute("INSERT INTO remember_event (word, remember_date) VALUES ('{}', strftime('%Y-%m-%d', '{}'))".format(word, remember_date))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} remember events, skip {} duplicated events.'.format(file, count, skip_count))

    def import_mistake_event(self, file, mistake_date):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        skip_count = 0
        for line in open(file):
            word = line[:line.find("|")]
            word = word.strip(' ')
            word = word.strip('\n')
            word = word.strip('\r')
            word = word.strip('\t')

            if len(word) == 0 :
                continue

            cursor.execute("SELECT count(1) FROM mistake_event WHERE word='{}' and mistake_date=strftime('%Y-%m-%d', '{}')".format(word, mistake_date))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated mistake event, word={} mistake_date={}.'.format(word, mistake_date))
                continue

            cursor.execute("INSERT INTO mistake_event (word, mistake_date) VALUES ('{}', strftime('%Y-%m-%d', '{}'))".format(word, mistake_date))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} mistake events, skip {} duplicated events.'.format(file, count, skip_count))

if __name__ == '__main__':
    utils = dbutils()

    #导入自定义的单词，多数是来自课堂笔记，一般是有特定意义的单词，如：MAP Math单词
    utils.import_dict('words/dict-MAP.txt', 'MAP')
    utils.import_dict('words/dict-KET.txt', 'KET')

    #导入单词标签，即单词的分类
    utils.import_word_tag('words/tag-KET.txt', 'KET')
    utils.import_word_tag('words/tag-MAP关键.txt', 'MAP关键')
    utils.import_word_tag('words/tag-MAP模拟题.txt', 'MAP模拟题')
    utils.import_word_tag('words/tag-newsela.txt', 'newsela')
    utils.import_word_tag('words/tag-WordlyWise2.txt', 'WordlyWise2')
    utils.import_word_tag('words/tag-俞敏洪初中.txt', '俞敏洪初中')
    utils.import_word_tag('words/tag-俞敏洪四级.txt', '俞敏洪四级')
    utils.import_word_tag('words/tag-俞敏洪高中.txt', '俞敏洪高中')
    utils.import_word_tag('words/tag-小学.txt', '小学')
    utils.import_word_tag('words/tag-简单词.txt', '简单词')

    #导入单词记忆事件
    utils.import_remember_event('words/remember-20200901.txt', '2020-09-01')
    utils.import_remember_event('words/remember-20201001.txt', '2020-10-01')
    utils.import_remember_event('words/remember-20201220.txt', '2020-12-20')
    utils.import_remember_event('words/remember-20201225.txt', '2020-12-25')
    utils.import_remember_event('words/remember-20210101.txt', '2021-01-01')
    utils.import_remember_event('words/remember-20210112.txt', '2021-01-12')
    utils.import_remember_event('words/remember-20210125.txt', '2020-01-25')
    utils.import_remember_event('words/remember-20210215.txt', '2021-02-15')
    utils.import_remember_event('words/remember-20210225.txt', '2021-02-25')
    utils.import_remember_event('words/remember-20210501.txt', '2021-05-01')
    utils.import_remember_event('words/remember-20210502.txt', '2021-05-02')

    #导入单词错词本
    utils.import_mistake_event('words/mistake-20210201.txt', '2021-02-01')


