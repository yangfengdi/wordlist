import sqlite3
from dictcn import dict_cn

class word_set():
    def __init__(self):
        pass

    # 按词频位置选择单词
    def word_by_freq(self, freq_type, pos_start, pos_end):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql="select word from word_freq where freq_type=? and pos between ? and ?"
        cursor.execute(sql, (freq_type, pos_start, pos_end))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 按tag选择单词
    def words_with_tag(self, tag):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word from word_tag where tag=?"
        cursor.execute(sql, (tag,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 记忆次数至少有（大于等于）指定数目的单词
    def words_min_remember_times(self, min_remember_times=1):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, count(1) from remember_event group by word having count(1)>=?"
        cursor.execute(sql, (min_remember_times,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 记忆次数最多有（小于等于）指定数目的单词
    def words_max_remember_times(self, max_remember_times=1):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, count(1) from remember_event group by word having count(1)<=?"
        cursor.execute(sql, (max_remember_times,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 最近记忆时间至少距今天（大于等于）指定天数的单词
    def words_min_last_remember_days(self, min_last_remember_days):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, min(round(julianday('now')-julianday(remember_date))) duration from remember_event group by word having duration>=？"
        cursor.execute(sql, (min_last_remember_days,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 最近记忆时间最多距今天（小于等于）指定天数的单词
    def words_max_last_remember_days(self, max_last_remember_days):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, min(round(julianday('now')-julianday(remember_date))) duration from remember_event group by word having duration<=？"
        cursor.execute(sql, (max_last_remember_days,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 指定测试结果次数至少有（大于等于）指定数目的单词
    def words_min_quiz_result_times(self, quiz_result, min_quiz_result_times=1):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, count(1) times from quiz_event where quiz_result=? group by word having times>=?"
        cursor.execute(sql, (quiz_result, min_quiz_result_times, ))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 只有失败的测试记录，或者最近的测试记录是失败的单词
    def words_last_quiz_fail(self):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        #最近的测试记录是失败的单词
        sql = '''select a.word from
                (select word, max(quiz_date) pass_date from quiz_event where quiz_result='PASS' group by word) a,
                (select word, max(quiz_date) fail_date from quiz_event where quiz_result='FAIL' group by word) b
                where a.word=b.word and fail_date>=pass_date'''
        cursor.execute(sql)
        result = set()
        for row in cursor:
            result.add(row[0])

        #只有测试失败记录，没有测试成功记录的单词
        sql = '''select distinct word from quiz_event a where quiz_result='FAIL' 
                and not exists (select 1 from quiz_event b where a.word=b.word and b.quiz_result='PASS')'''
        cursor.execute(sql)
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    #一个简单的分词器
    def __split_words(self, str):
        #分词自动机：
        #状态0（初态）：字母和减号-->1；其它字符-->0
        #状态1（在词语中）：字母和减号-->1；其它字符-->0
        result = set()
        curr_word = ''
        curr_state = 0

        for idx in range(0, len(str)):
            if curr_state == 0:
                if str[idx] in ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
                    curr_state = 1
                    curr_word = str[idx]
                else:
                    pass
            else:
                if str[idx] in ('-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
                    #curr_state = 1
                    curr_word = curr_word + str[idx]
                else:
                    curr_state = 0
                    result.add(curr_word)
                    curr_word = ''

        if len(curr_word) > 0:
            result.add(curr_word)

        return result

    def words_in_artical(self, file):
        result = set()
        for line in open(file):
            roughWords = self.__split_words(line)
            for roughWord in roughWords:
                if len(roughWord) <= 1:
                    continue

                result.add(roughWord)
        return result

    def words_in_list(self, file):
        result = set()
        for line in open(file):
            if line.find('|') == -1:
                word = line
            else:
                word = line[:line.find('|')]

            if len(word) > 0:
                result.add(word)
        return result

    def __filter_words(self, rough_words):
        words_except = self.words_with_tag('简单词')
        words_except = words_except|self.words_with_tag('小学')
        words_except = words_except|self.words_with_tag('俞敏洪初中')
        #words_except = words_except|self.words_with_tag('俞敏洪高中')

        words_variant = self.words_with_tag('复数')
        words_variant = words_variant|self.words_with_tag('第三人称单数')
        words_variant = words_variant|self.words_with_tag('过去式')
        words_variant = words_variant|self.words_with_tag('过去分词')
        words_variant = words_variant|self.words_with_tag('现在分词')
        words_variant = words_variant|self.words_with_tag('比较级')
        words_variant = words_variant|self.words_with_tag('最高级')

        words_proper = self.words_with_tag('姓氏')
        words_proper = words_proper|self.words_with_tag('人名')
        words_proper = words_proper|self.words_with_tag('国名')
        words_proper = words_proper|self.words_with_tag('美国州名')
        words_proper = words_proper|self.words_with_tag('城市')
        words_proper = words_proper|self.words_with_tag('缩写')

        dictcn = dict_cn()
        words_in_artical = set()
        words_meaning = {}
        for word in rough_words - words_except - words_variant:
            meaning = ''
            dict_word, meaning = dictcn.search(word)
            words_meaning[dict_word] = meaning
            words_in_artical.add(dict_word)

        words_first_letter_capital = self.words_with_tag('首字母大写')

        words_top_freq = self.word_by_freq('BE', 0, 20000)|self.word_by_freq('AE', 0, 20000)

        words_remembered = self.words_min_remember_times()

        words_in_artical = words_in_artical - words_except #去除某些简单单词，如小学、初中单词等
        words_in_artical = words_in_artical - words_variant  #去除变体的单词
        words_in_artical = words_in_artical - words_proper #去除专用单词，如：国名、地名、人名等
        words_in_artical = words_in_artical - words_first_letter_capital #去除首字母大写单词
        words_in_artical = words_in_artical - words_remembered #去除曾经记忆过的单词

        count = 0
        for word in words_in_artical: #不筛除低频词
        #for word in words_in_artical&words_top_freq:  #筛除低频词
            with open("words/newword.txt", 'a') as f:
                f.write('{}|{}'.format(word, words_meaning[word]) + '\n')
                # f.write('{}'.format(word.word) + '\n')
            count += 1

    def get_new_words_from_artical(self, file):
        rough_words_in_artical = self.words_in_artical(file)
        self.__filter_words(rough_words_in_artical)

    def get_new_words_from_list(self, file):
        rough_words_in_list = self.words_in_list(file)
        self.__filter_words(rough_words_in_list)

    def get_new_words_from_list_without_filter(self, file):
        rough_words_in_list = self.words_in_list(file)

        dictcn = dict_cn()
        for word in rough_words_in_list:
            dict_word, meaning = dictcn.search(word)
            if len(dict_word) == 0:
                continue
            with open("words/newword.txt", 'a') as f:
                f.write('{}|{}'.format(dict_word, meaning) + '\n')

    def get_review_words_from_fail_record(self):
        words = self.words_last_quiz_fail()
        words_remembered = self.words_min_remember_times(3)

        count = 0
        for word in words-words_remembered:
            count += 1
            #print('[{}]={}'.format(count, word))
            print(word)

    def get_new_words_from_top_freq(self):
        rough_top_freq_words = self.word_by_freq('BE', 0, 1800)
        self.__filter_words(rough_top_freq_words)

if __name__ == '__main__':
    word_set = word_set()
    #word_set.get_new_words_from_artical('words/article-mars.txt')
    #word_set.get_new_words_from_list('words/words.txt')
    #word_set.get_review_words_from_fail_record()
    #word_set.get_new_words_from_top_freq()

    word_set.get_new_words_from_list_without_filter('words/words.txt')

