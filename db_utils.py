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
                    quiz_result = sections[3][12:]

                    if quiz_result != 'P' and quiz_result != 'F':
                        continue

                    # print('{}={}'.format(word, quiz_result))

                    if len(word) == 0:
                        continue

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

        conn.close()
        print('import files in {} completed, add {} quiz events, skip {} duplicated events.'.format(dir, count, skip_count))

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
