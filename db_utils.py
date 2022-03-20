import sqlite3
import os

class db_utils():

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

    def import_remember_events(self, dir):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        dirs = os.listdir( dir )
        count = 0
        skip_count = 0
        for file in dirs:
            if file.upper().startswith('REMEMBER') and file.upper().endswith('.TXT'):
                remember_file = '{}/{}'.format(dir, file)
                remember_date = '{}-{}-{}'.format(file[9:13], file[13:15], file[15:17])
                #print('remember date = {}'.format(remember_date))
                for line in open(remember_file):
                    word = line[:line.find("|")]
                    word = word.strip(' ')
                    word = word.strip('\n')
                    word = word.strip('\r')
                    word = word.strip('\t')

                    if len(word) == 0:
                        continue

                    cursor.execute(
                        "SELECT count(1) FROM remember_event WHERE word='{}' and remember_date=strftime('%Y-%m-%d', '{}')".format(
                            word, remember_date))
                    if cursor.fetchone()[0] != 0:
                        skip_count += 1
                        # print('skip duplicated remember event, word={} remember_date={}.'.format(word, remember_date))
                        continue

                    cursor.execute(
                        "INSERT INTO remember_event (word, remember_date) VALUES ('{}', strftime('%Y-%m-%d', '{}'))".format(
                            word, remember_date))
                    conn.commit()
                    count += 1
        conn.close()
        print('import files in {} completed, add {} remember events, skip {} duplicated events.'.format(dir, count, skip_count))

    def import_quiz_result(self, dir):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        dirs = os.listdir( dir )
        count = 0
        skip_count = 0
        for file in dirs:
            if file.upper().startswith('QUIZ') and file.upper().endswith('.TXT'):
                quiz_file = '{}/{}'.format(dir, file)
                quiz_date = '{}-{}-{}'.format(file[5:9], file[9:11], file[11:13])

                pass_in_file = 0
                fail_in_file = 0
                for line in open(quiz_file):
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
                    quiz_result = sections[3][12:13].upper()

                    # if quiz_result != 'P' and quiz_result != 'F':
                    #     continue

                    #print('{}={}'.format(word, quiz_result))

                    if len(word) == 0:
                        continue


                    if quiz_result == 'P':
                        pass_in_file += 1
                    else:
                        fail_in_file += 1

                    sql = "SELECT count(1) FROM quiz_event WHERE word=? and quiz_date=strftime('%Y-%m-%d', ?)"
                    cursor.execute(sql, (word, quiz_date,))
                    if cursor.fetchone()[0] != 0:
                        skip_count += 1
                        #print('skip duplicated quiz event, word={} quiz_date={}.'.format(word, quiz_date))
                        continue

                    if quiz_result == 'P':
                        sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), 'PASS')"
                        #print('word={} PASS'.format(word))
                    else:
                        sql = "INSERT INTO quiz_event (word, quiz_date, quiz_result) VALUES (?, strftime('%Y-%m-%d', ?), 'FAIL')"
                        #print('word={} FAIL'.format(word))
                    cursor.execute(sql, (word, quiz_date,))
                    conn.commit()
                    count += 1

                print('{}测验：通过率={}/%，通过={}，失败={}，'.format(quiz_date, round(pass_in_file * 100 / (pass_in_file + fail_in_file)), pass_in_file, fail_in_file))

        conn.close()
        print('import files in {} completed, add {} quiz events, skip {} duplicated events.'.format(dir, count, skip_count))

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

    # 导入待安排记忆计划的单词，为系统制定细化到每天的quizlet set计划做准备
    # file：待导入的词库文件，可以是每行一个单词，也可以每行用|分隔单词与释义，释义不会被采用
    # word_type：指明导入的单词是新词(NEW)还是旧词(OLD)，
    #            是新词还是旧词与系统中是否存在记忆记录无关，
    #            会被保存在word_remember_plan.word_type中，在自动制定计划的时候会用到，
    #            自动制定计划的时候可以指定每天包含多少个新词，到时候就会用到这个数据
    # gap_days:是保存一个单词多次背诵的时间间隔的元组，用于制定单词背诵计划
    #          如(2,5,0)表示一个单词需要背3次，第一次背完之后过2天（隔1天）再背第二次，第二次背完之后过5天再背第三次
    #          艾宾浩斯的记忆法建议的计划计划是分别在第1、2、4、7、15记忆，换算成gap_day元组就是(1, 2, 3, 8, 0)
    #          对于有些曾经背过多次的单词，如果需要做强化复习，可以不需要完全按照艾宾浩斯的曲线来记忆，可以酌情考虑记忆次数与每次记忆间隔时间
    #          每个单词规划的记忆次数限定为不超过5次
    def import_word_remember_plan(self, file, word_type, gap_days):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        if len(gap_days)>5:
            print('单词的规划记忆次数不可超过5次')

        count = 0
        skip_count = 0
        for word in open(file):
            word = word[:word.find("|")]
            word = word.strip(' ')
            word = word.strip('\n')
            word = word.strip('\r')
            word = word.strip('\t')

            #print(word)

            cursor.execute("SELECT count(1) FROM word_remember_plan WHERE word='{}'".format(word))
            if cursor.fetchone()[0] != 0:
                skip_count += 1
                continue

            for seq in range(len(gap_days)):
                sql = "INSERT INTO word_remember_plan (word, word_type, seq_no, gap_days, plan_status) " \
                    "VALUES (?, ?, ? , ?, 'UNPLANNED')"
                cursor.execute(sql,(word,word_type, seq, gap_days[seq]))
                conn.commit()

            count += 1

        conn.close()
        print('import file {} completed, add {} plan remember new word, skip {} words.'.format(file, count, skip_count))

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
