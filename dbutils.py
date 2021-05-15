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

    def import_quiz_event(self, file, quiz_date):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        skip_count = 0
        line_no = 0
        for line in open(file):
            line_no += 1
            word = line[:line.find("|")]
            word = word.strip(' ')
            word = word.strip('\n')
            word = word.strip('\r')
            word = word.strip('\t')

            abbr_result = line[line.find("|"):]
            abbr_result = abbr_result.strip(' ')
            abbr_result = abbr_result.strip('\n')
            abbr_result = abbr_result.strip('\r')
            abbr_result = abbr_result.strip('\t')

            quiz_result = ''
            if abbr_result == 'P':
                quiz_result = 'PASS'
            elif abbr_result == 'F':
                quiz_result = 'FAIL'
            else:
                print('unexcepted result {} in line {}, skiped.'.format(abbr_result, line_no))
                continue

            if len(word) == 0 :
                continue

            sql = "SELECT count(1) FROM quiz_event WHERE word=? and quiz_date=strftime('%Y-%m-%d', ?) and quiz_result=?"
            cursor.execute(sql,(word, quiz_date, quiz_result,))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated mistake event, word={} mistake_date={}.'.format(word, mistake_date))
                continue

            sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), ?)"
            cursor.execute(sql, (word, quiz_date, quiz_result))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} quiz events, skip {} duplicated events.'.format(file, count, skip_count))

    def import_quiz_fail_event(self, file, quiz_date):
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

            sql = "SELECT count(1) FROM quiz_event WHERE word=? and quiz_date=strftime('%Y-%m-%d', ?) and quiz_result='FAIL'"
            cursor.execute(sql,(word, quiz_date,))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated mistake event, word={} mistake_date={}.'.format(word, mistake_date))
                continue

            sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), 'FAIL')"
            cursor.execute(sql, (word, quiz_date,))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} quiz events, skip {} duplicated events.'.format(file, count, skip_count))

    def import_quiz_pass_event(self, file, quiz_date):
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

            sql = "SELECT count(1) FROM quiz_event WHERE word=? and quiz_date=strftime('%Y-%m-%d', ?) and quiz_result='PASS'"
            cursor.execute(sql,(word, quiz_date,))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated mistake event, word={} mistake_date={}.'.format(word, mistake_date))
                continue

            sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), 'PASS')"
            cursor.execute(sql, (word, quiz_date,))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} quiz events, skip {} duplicated events.'.format(file, count, skip_count))

    def import_quiz_result(self, file, quiz_date):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        skip_count = 0
        for line in open(file):
            if len(line.strip(' ')) == 0:
                continue

            if line.strip(' ').startswith('##'):
                continue

            line = line.strip(' ')
            line = line.strip('\n')
            line = line.strip('\r')
            line = line.strip('\t')
            sections = line.split('|')
            if len(sections) != 4:
                continue

            word = sections[1][5:]
            quiz_result = sections[3][12:]

            if quiz_result != 'P' and quiz_result != 'F':
                continue

            #print('{}={}'.format(word, quiz_result))

            if len(word) == 0 :
                continue

            sql = "SELECT count(1) FROM quiz_event WHERE word=? and quiz_date=strftime('%Y-%m-%d', ?)"
            cursor.execute(sql,(word, quiz_date,))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                #print('skip duplicated mistake event, word={} mistake_date={}.'.format(word, mistake_date))
                continue

            if quiz_result == 'P':
                sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), 'PASS')"
            else:
                sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), 'FAIL')"
            cursor.execute(sql, (word, quiz_date,))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} quiz events, skip {} duplicated events.'.format(file, count, skip_count))

    def import_word_freq(self, file, freq_type):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        count = 0
        for word in open(file):
            word = word.strip('\n')
            word = word.strip('\r')
            word = word.strip('\t')
            word = word.strip(' ')
            #print(word)
            #print(result[1])
            sql = "INSERT INTO word_freq (pos, word, freq_type) VALUES (?, ?, ?)"
            cursor.execute(sql,(count+1, word, freq_type))
            conn.commit()
            count += 1

        conn.close()
        print('import file {} completed, add {} word freq records.'.format(file, count))

if __name__ == '__main__':
    utils = dbutils()

    #导入SUBTLEXus美国英语词频库
    #utils.import_word_freq('words/美国英语词频库(SUBTLEXus).txt', 'AE')

    #导入BNC英国英语词频库
    #utils.import_word_freq('words/英国英语词频库(BNC).txt', 'BE')

    #导入自定义词典，多数是来自课堂笔记，一般是有特定意义的单词，如：MAP Math单词
    #utils.import_dict('words/dict-MAP.txt', 'MAP')
    #utils.import_dict('words/dict-KET.txt', 'KET')

    #导入单词标签，即单词的分类
    #utils.import_word_tag('words/tag-KET.txt', 'KET')
    #utils.import_word_tag('words/tag-MAP关键.txt', 'MAP关键')
    #utils.import_word_tag('words/tag-MAP模拟题.txt', 'MAP模拟题')
    #utils.import_word_tag('words/tag-newsela.txt', 'newsela')
    #utils.import_word_tag('words/tag-WordlyWise2.txt', 'WordlyWise2')
    #utils.import_word_tag('words/tag-俞敏洪初中.txt', '俞敏洪初中')
    #utils.import_word_tag('words/tag-俞敏洪四级.txt', '俞敏洪四级')
    #utils.import_word_tag('words/tag-俞敏洪高中.txt', '俞敏洪高中')
    #utils.import_word_tag('words/tag-小学.txt', '小学')
    #utils.import_word_tag('words/tag-简单词.txt', '简单词')

    #导入单词记忆事件
    #utils.import_remember_event('words/remember-20200901.txt', '2020-09-01')
    #utils.import_remember_event('words/remember-20201001.txt', '2020-10-01')
    #utils.import_remember_event('words/remember-20201220.txt', '2020-12-20')
    #utils.import_remember_event('words/remember-20201225.txt', '2020-12-25')
    #utils.import_remember_event('words/remember-20210101.txt', '2021-01-01')
    #utils.import_remember_event('words/remember-20210112.txt', '2021-01-12')
    #utils.import_remember_event('words/remember-20210125.txt', '2021-01-25')
    #utils.import_remember_event('words/remember-20210215.txt', '2021-02-15')
    #utils.import_remember_event('words/remember-20210225.txt', '2021-02-25')
    #utils.import_remember_event('words/remember-20210501.txt', '2021-05-01')
    #utils.import_remember_event('words/remember-20210502.txt', '2021-05-02')
    #utils.import_remember_event('words/remember-20210503.txt', '2021-05-03')
    #utils.import_remember_event('words/remember-20210504.txt', '2021-05-04')
    #utils.import_remember_event('words/remember-20210505.txt', '2021-05-05')
    #utils.import_remember_event('words/remember-20210506.txt', '2021-05-06')
    #utils.import_remember_event('words/remember-20210507.txt', '2021-05-07')
    #utils.import_remember_event('words/remember-20210508.txt', '2021-05-08')
    #utils.import_remember_event('words/remember-20210510.txt', '2021-05-10')
    #utils.import_remember_event('words/remember-20210511.txt', '2021-05-11')
    #utils.import_remember_event('words/remember-20210512.txt', '2021-05-12')
    #utils.import_remember_event('words/remember-20210513.txt', '2021-05-13')
    #utils.import_remember_event('words/remember-20210514.txt', '2021-05-14')

    #导入单词错词本
    #utils.import_quiz_fail_event('words/fail-20210201.txt', '2021-02-01')
    utils.import_quiz_result('words/quiz-20210516.txt', '2021-05-16')

