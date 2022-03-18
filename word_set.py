import sqlite3
import os
import docx
from dictcn import dict_cn
import random

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor

class word_set():
    def __init__(self):
        pass


    def get_new_words_from_docxs(self, dir):
        dirs = os.listdir( dir )
        rough_words_in_docx = set()
        for file in dirs:
            if file.upper().endswith('.DOCX'):
                docfile = docx.Document("{}/{}".format(dir, file))
                for para in docfile.paragraphs:
                    rough_words_in_para = self.__split_words(para.text)
                    for rough_word in rough_words_in_para:
                        if len(rough_word) <= 1:
                            continue
                        rough_words_in_docx.add(rough_word)

        #print(rough_words_in_docx)
        dictcn = dict_cn()
        words = set()
        for word in rough_words_in_docx:
            dict_word, meaning = dictcn.search(word)
            words.add(dict_word)

        words_count = len(words)
        print('从文章中读取到 {} 个单词'.format(words_count))

        words = words - self.words_last_quiz_pass() #如果一个词最近一次测验是通过的就跳过
        print('剔除测验通过的 {} 个单词，剩余 {} 个单词'.format(words_count - len(words), len(words)))
        words_count = len(words)

        words = words - self.words_min_remember_times(1) #如果一个词曾经被背过一定次数以上就跳过
        print('剔除曾经背过的 {} 个单词，剩余 {} 个单词'.format(words_count - len(words), len(words)))

        words_dict = self.__filter_words(words)
        print('最终输出 {} 个新词'.format(len(words_dict)))

        self.__write_dict_to_file(words_dict, "words/newword.txt")

    def get_words_from_article(self, file):
        rough_words_in_article = self.words_in_artical(file)
        dictcn = dict_cn()
        words = {}

        for word in rough_words_in_article:
            dict_word, meaning = dictcn.search(word)
            words[dict_word] = meaning

        self.__write_dict_to_file(words, "words/newword.txt")

    def get_new_words_from_articles(self, dir):
        dirs = os.listdir( dir )
        rough_words_in_articals = set()
        for file in dirs:
            if file.upper().endswith('.TXT'):
                rough_words_in_articals = rough_words_in_articals | self.words_in_artical("{}/{}".format(dir, file))

        dictcn = dict_cn()
        words = set()
        for word in rough_words_in_articals:
            dict_word, meaning = dictcn.search(word)
            words.add(dict_word)

        words_count = len(words)
        print('从文章中读取到 {} 个单词'.format(words_count))

        words = words - self.words_last_quiz_pass() #如果一个词最近一次测验是通过的就跳过
        print('剔除测验通过的 {} 个单词，剩余 {} 个单词'.format(words_count - len(words), len(words)))
        words_count = len(words)

        words = words - self.words_min_remember_times(1) #如果一个词曾经被背过一定次数以上就跳过
        print('剔除曾经背过的 {} 个单词，剩余 {} 个单词'.format(words_count - len(words), len(words)))

        words_dict = self.__filter_words(words)
        print('最终输出 {} 个新词'.format(len(words_dict)))
        self.__write_dict_to_file(words_dict, "words/newword.txt")

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

        sql = "select word, min(round(julianday('now')-julianday(remember_date))) duration from remember_event group by word having duration>=?"
        cursor.execute(sql, (min_last_remember_days,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 在最近指定的时间范围内（天数）做过测试的单词
    def words_recent_quiz(self, quiz_duration):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, min(round(julianday('now')-julianday(quiz_date))) duration from quiz_event group by word having duration<=?"
        cursor.execute(sql, (quiz_duration,))

        result = set()
        for row in cursor:
            result.add(row[0])

        conn.close()
        return result

    # 最近记忆时间最多距今天（小于等于）指定天数的单词
    def words_max_last_remember_days(self, max_last_remember_days):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        sql = "select word, min(round(julianday('now')-julianday(remember_date))) duration from remember_event group by word having duration<=?"
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

    # 只有成功的测试记录，或者最近的测试记录是成功的单词
    def words_last_quiz_pass(self):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        #最近的测试记录是成功的单词
        sql = '''select a.word from
                (select word, max(quiz_date) pass_date from quiz_event where quiz_result='PASS' group by word) a,
                (select word, max(quiz_date) fail_date from quiz_event where quiz_result='FAIL' group by word) b
                where a.word=b.word and fail_date<pass_date'''
        cursor.execute(sql)
        result = set()
        for row in cursor:
            result.add(row[0])

        #只有测试成功记录，没有测试失败记录的单词
        sql = '''select distinct word from quiz_event a where quiz_result='PASS' 
                and not exists (select 1 from quiz_event b where a.word=b.word and b.quiz_result='FAIL')'''
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
                if str[idx] in ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
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
        dictcn = dict_cn()
        words_list = set()
        words_meaning = {}
        for word in rough_words:
            meaning = ''
            dict_word, meaning = dictcn.search(word)
            words_meaning[dict_word] = meaning
            words_list.add(dict_word)

        words_except = self.words_with_tag('简单词')
        words_except = words_except|self.words_with_tag('小学')
        words_except = words_except|self.words_with_tag('俞敏洪初中')
        words_except = words_except|self.words_with_tag('俞敏洪高中')

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

        words_first_letter_capital = self.words_with_tag('首字母大写')

        words_top_freq = self.word_by_freq('BE', 0, 15000)|self.word_by_freq('AE', 0, 15000)

        words_count = len(words_list)

        words_list = words_list - words_except #去除某些简单单词，如小学、初中单词等
        print('剔除 {} 个小学词汇、初中词汇等简单单词，剩余 {} 个单词'.format(words_count - len(words_list), len(words_list)))
        words_count = len(words_list)

        words_list = words_list - words_variant  #去除变体的单词
        print('剔除 {} 个复数、过去式、过去分词等变体单词，剩余 {} 个单词'.format(words_count - len(words_list), len(words_list)))
        words_count = len(words_list)

        words_list = words_list - words_proper #去除专用单词，如：国名、地名、人名等
        print('剔除 {} 个国名、地名、人名等专有词汇，剩余 {} 个单词'.format(words_count - len(words_list), len(words_list)))
        words_count = len(words_list)

        words_list = words_list - words_first_letter_capital #去除首字母大写单词
        print('剔除 {} 个首字母大写，剩余 {} 个单词'.format(words_count - len(words_list), len(words_list)))
        words_count = len(words_list)

        words_list = words_list & words_top_freq #剔除低频词
        print('剔除 {} 个词频低于 美语TOP15000 的低频单词，剩余 {} 个单词'.format(words_count - len(words_list), len(words_list)))

        result = {}
        for word in words_list:
            result[word] = words_meaning[word]
        return result

    def __write_dict_to_file(self, dict, file):
        for word in dict.keys(): #不筛除低频词
            with open(file, 'a') as f:
                f.write('{}|{}'.format(word, dict[word]) + '\n')

    def get_new_words_from_list(self, file):
        dictcn = dict_cn()
        rough_words_in_artical = self.words_in_list(file)
        words = set()
        for word in rough_words_in_artical:
            dict_word, meaning = dictcn.search(word)
            words.add(dict_word)

        words = words - self.words_min_remember_times(2) #如果一个词曾经被背过一定次数以上就跳过
        words = words - self.words_last_quiz_pass()  # 如果一个词最近一次测验是通过的就跳过
        words_dict = self.__filter_words(words)
        self.__write_dict_to_file(words_dict, "words/newword.txt")

    def get_new_words_from_list_without_filter(self, file):
        rough_words_in_list = self.words_in_list(file)

        words = {}
        dictcn = dict_cn()
        for word in rough_words_in_list:
            dict_word, meaning = dictcn.search(word)
            if len(dict_word) == 0:
                continue
            words[dict_word] = meaning
        self.__write_dict_to_file(words, "words/newword.txt")

    def get_review_words_from_fail_record(self):
        fail_words = self.words_last_quiz_fail()
        words_remembered = self.words_min_remember_times(5)

        words = {}
        dictcn = dict_cn()
        for word in fail_words - words_remembered:
            dict_word, meaning = dictcn.search(word)
            if len(dict_word) == 0:
                continue
            words[dict_word] = meaning
        self.__write_dict_to_file(words, "words/newword.txt")

    def get_new_words_from_top_freq(self):
        words = self.word_by_freq('AE', 0, 2000)
        words = words - self.words_min_remember_times(2)  # 如果一个词曾经被背过一定次数以上就跳过
        words = words - self.words_last_quiz_pass()  # 如果一个词最近一次测验是通过的就跳过
        words_dict = self.__filter_words(words)
        self.__write_dict_to_file(words_dict, "words/newword.txt")

    def get_words_from_tag(self, tag):
        words = self.words_with_tag(tag)
        words = words - self.words_min_remember_times(2)  # 如果一个词曾经被背过2次以上就跳过
        words = words - self.words_last_quiz_pass()  # 如果一个词最近一次测验是通过的就跳过
        words_dict = self.__filter_words(words)
        self.__write_dict_to_file(words_dict, "words/newword.txt")

    def get_words_from_recent_remember_words(self):
        words = self.words_max_last_remember_days(7) #最近7天以内背过的单词
        words = words - self.words_min_remember_times(2)  # 如果一个词曾经被背过2次以上就跳过
        words = words - self.words_last_quiz_pass()  # 如果一个词最近一次测验是通过的就跳过
        words_dict = self.__filter_words(words)
        self.__write_dict_to_file(words_dict, "words/newword.txt")

    def __create_random_mapping_for_quiz(self, size):
        result = {}
        reversed_result = {}

        num_use = {}
        for i in range(0, size):
            num_use[i] = False

        pos = 0
        for i in range(0, size):
            steps = random.randint(1, size - i)

            for step in range(0, steps):
                pos += 1
                if pos >= size :
                    pos = pos % size
                while num_use[pos] == True:
                    pos += 1
                    if pos >= size :
                        pos = pos % size

            num_use[pos] = True

            result[i] = pos
            reversed_result[pos] = i

        return result, reversed_result

    def make_quiz_from_fail_record(self, start_date, page_max = 10):
        words = self.words_last_quiz_fail()
        words = words - self.words_max_last_remember_days(30) #最近30天内背过的单词不测验
        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        self.__make_quiz(words, start_date, page_max)

    def make_quiz_from_tag(self, words_tag, start_date, page_max = 10):
        words = self.words_with_tag(words_tag)
        word_count = len(words)
        print('初始获得 {} 个单词'.format(word_count))

        words = words - self.words_max_last_remember_days(30) #最近15天内背过的单词不测验
        print('剔除 {} 个最近30内记忆过的单词，剩余 {} 个单词'.format(word_count - len(words), len(words)))
        word_count = len(words)

        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        print('剔除 {} 个最近一次测验通过的单词，剩余 {} 个单词'.format(word_count - len(words), len(words)))
        word_count = len(words)

        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        print('剔除 {} 个最近30天内做过测验的单词，剩余 {} 个单词'.format(word_count - len(words), len(words)))

        self.__make_quiz(words, start_date, page_max)

    def make_quiz_from_list(self, file, start_date, page_max = 10):
        words = self.words_in_list(file)

        word_count = len(words)
        print('初始获得 {} 个单词'.format(word_count))

        words = words - self.words_max_last_remember_days(30) #最近15天内背过的单词不测验
        print('剔除 {} 个最近30内记忆过的单词，剩余 {} 个单词'.format(word_count - len(words), len(words)))
        word_count = len(words)

        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        print('剔除 {} 个最近一次测验通过的单词，剩余 {} 个单词'.format(word_count - len(words), len(words)))
        word_count = len(words)

        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        print('剔除 {} 个最近30天内做过测验的单词，剩余 {} 个单词'.format(word_count - len(words), len(words)))

        self.__make_quiz(words, start_date, page_max, filter=False)

    def make_quiz_from_remembered_some_days_words(self, start_date, page_max=10):
        words = self.words_min_remember_times(2) #至少背过3次的单词
        words = words & self.words_min_last_remember_days(30) #最近一次记忆是在30天以前
        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        self.__make_quiz(words, start_date, page_max)

    def __make_quiz(self, words, start_date, page_max = 10, filter = True):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()
        words_list = set()
        words_meaning = {}

        dictcn = dict_cn()
        for word in words:
            dict_word, meaning = dictcn.search(word)
            words_meaning[dict_word] = meaning
            words_list.add(dict_word)

        if filter :
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

            words_first_letter_capital = self.words_with_tag('首字母大写')

            word_count = len(words_list)

            self.__print_word_list(words_list & words_variant)
            words_list = words_list - words_variant  #去除变体的单词
            print('剔除 {} 个变体单词，剩余 {} 个单词'.format(word_count - len(words_list), len(words_list)))
            word_count = len(words_list)

            self.__print_word_list(words_list & words_proper)
            words_list = words_list - words_proper #去除专用单词，如：国名、地名、人名等
            print('剔除 {} 个国名、地名等专有单词，剩余 {} 个单词'.format(word_count - len(words_list), len(words_list)))
            word_count = len(words_list)

            self.__print_word_list(words_list & words_first_letter_capital)
            words_list = words_list - words_first_letter_capital #去除首字母大写单词
            print('剔除 {} 个首字母大写单词，剩余 {} 个单词'.format(word_count - len(words_list), len(words_list)))

        self.__print_word_list(words_list)
        print('最终输出 {} 个单词'.format(len(words_list)))

        words_dict = {}
        for word in words_list:
            words_dict[word] = words_meaning[word]

        chinese_number = ['0', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
        roman_number = ['0', 'Ⅰ.', 'Ⅱ.', 'Ⅲ.', 'Ⅳ.', 'Ⅴ.', 'Ⅵ.', 'Ⅶ.', 'Ⅷ.', 'Ⅸ.', 'Ⅹ.']
        pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))

        words_per_page = 6
        quiz_words = {}
        quiz_meanings = {}
        quiz_meanings_disorder = {}
        inside_page_index = 0
        page_no = 0

        pdf_filename = ""
        txt_filename = ""
        canv = None
        for word in words_dict.keys():
            if page_no % page_max == 0:
                if round(page_no / page_max) > 0:
                    canv.save()

                #获取quiz的日期字符串，此处借用sqlite来进行计算
                sql = "select strftime('%Y%m%d', date(?, ?)) "
                #print(sql, start_date, '+{} day'.format(round(page_no / page_max)) )
                cursor.execute(sql, (start_date, '+{} day'.format(round(page_no / page_max)), ))
                row = cursor.fetchone()
                cmp_date_str = row[0] #YYYYMMDD格式的日期字符串

                pdf_filename = "words/plan/quiz-{}.pdf".format(cmp_date_str)
                txt_filename = "words/plan/quiz-{}.txt".format(cmp_date_str)
                canv = canvas.Canvas(pdf_filename)

            if inside_page_index == words_per_page:
                inside_page_index = 0
                page_no += 1

                style = ParagraphStyle(name='normal')
                style.fontSize = 20
                style.fontName = "SimSun"
                style.alignment = 1

                display_page_no = page_no % page_max
                if display_page_no == 0:
                    display_page_no = page_max

                p = Paragraph("单词练习-{}".format(display_page_no), style)
                p.wrap(210 * mm, 35 * mm)
                p.drawOn(canv, 0, 292 * mm)

                with open(txt_filename, 'a') as f:
                    f.write('##Page-{}'.format(display_page_no) + '\n')

                canv.setFont("SimSun", 18)

                quiz_mapping, reversed_quiz_mapping = self.__create_random_mapping_for_quiz(words_per_page)
                for i in range(0, words_per_page):
                    quiz_meanings_disorder[i] = quiz_meanings[quiz_mapping[i]]

                for i in range(0, words_per_page):
                    style = ParagraphStyle(name='normal')
                    style.backColor = HexColor(0xEEEEEE)
                    style.fontSize = 18
                    style.fontName = "SimSun"
                    style.leading = 18
                    p = Paragraph('{}{}'.format(roman_number[i + 1], quiz_words[i]), style)
                    word_width, word_height = p.wrap(75 * mm, 40 * mm)
                    p.drawOn(canv, 0.5 * mm, (270 - i * 45) * mm - word_height)

                    style = ParagraphStyle(name='normal')
                    style.backColor = HexColor(0xEEEEEE)
                    style.fontSize = 10
                    style.fontName = "SimSun"
                    style.leading = 18
                    p = Paragraph('Answer:<br/><br/><br/>_________________________________________', style)
                    answer_width, answer_height = p.wrap(75 * mm, 40 * mm)
                    p.drawOn(canv, 0.5 * mm, (270 - i * 45) * mm - word_height - answer_height - 10)

                    with open(txt_filename, 'a') as f:
                        f.write('{}|word={}|meaning={}|result(P/F)=\n'.format(roman_number[i + 1], quiz_words[i], chinese_number[reversed_quiz_mapping[i] + 1]))
                        #print('{}word={}|meaning={}'.format(roman_number[i + 1], quiz_words_disorder[i], chinese_number[reversed_quiz_mapping[i] + 1]))

                with open(txt_filename, 'a') as f:
                    f.write('\n')

                for i in range(0, words_per_page):
                    style = ParagraphStyle(name='normal')
                    style.backColor = HexColor(0xEEEEEE)
                    style.fontSize = 18
                    style.fontName = "SimSun"
                    style.leading = 18

                    p = Paragraph('{}{}'.format(chinese_number[i + 1], quiz_meanings_disorder[i]), style)
                    meaning_width, meaning_height = p.wrap(110 * mm, 40 * mm)
                    p.drawOn(canv, 100 * mm, (270 - i * 45) * mm - meaning_height)

                    #print('{}meaning={}'.format(chinese_number[i+1], quiz_meanings_disorder[i]))

                canv.showPage()
                canv.setFont("SimSun", 18)

            quiz_words[inside_page_index] = word
            quiz_meanings[inside_page_index] = words_dict[word]
            inside_page_index += 1

        canv.save()

    # 自动为要制定背诵计划的单词生成每日的quizlet set
    # 计划要记忆的单词都被保存在word_remember_plan中，有新词也有旧词，保存在word_type字段中
    # start_date：记忆起始日期，制定的quizlet set的起始时间是从这一天开始的，
    #             如果此前曾经制定过start_date日期及以后时间的记忆计划，则记忆计划会被清除，
    #             并基于最新的要记忆的单词和参数重新计划，但是原来自动生成的remember-YYYYMMDD.txt文件不会自动删除，需要手工处理
    # set_size：quizlet set的大小，也就是每天背多少个单词，含新词和复习旧词的总数
    # new_word_cnt：每天的quizlet set中添加的新词的数目
    #               设置new_word_cnt需要认真考虑与set_size的相对大小，
    #               举个例子：如果单词采用标准的艾宾浩斯记忆法来记（取决于准备单词时调用db_utils.import_word_remember_plan的gap_days参数），
    #               每个单词需要被记5次，只有第一次被记忆的时候被认为是新词，其余4次记忆都是复习，
    #               这意味着new_word_cnt最多只能有set_size的1/5，否则会出现每次加入过大比例的新词，造成旧词复习进度不能按时完成的情况
    #               如果掺杂了一些需要复习的旧词，则new_word_cnt需要设置得更小一些，才能把旧词消化掉
    # 在系统自动制定每天的单词quizlet set背诵计划的时候，会尽量按照为每个单词在db_utils.import_word_remember_plan
    # 导入词汇到系统时所指定的gap_days安排背诵的间隔时间规划每天的quizlet set，但是受限于quizlet size参数的限制，并不能确保每个单词都能按理想的时间被安排记忆
    # 在word_remember_plan表中，实际被规划记忆的时间被保存在plan_remember_date字段，严格按照gap_days设定的背诵时间被保存在ideal_remember_date字段
    # 通过对比plan_remember_date和ideal_remember_date两个时间的差距，可以评估计划算法的效果，一般来说，只要参数选择合理，
    # word_remember_plan表中会有超过一半的记录的plan_remember_date和ideal_remember_date两个时间之差为0
    def create_quizlet_set(self, start_date, set_size, new_word_cnt):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()
        old_word_cnt = set_size - new_word_cnt

        sql = "update word_remember_plan set plan_status='UNPLANNED', " \
              "plan_remember_date=NULL where plan_remember_date>=date(?)"
        cursor.execute(sql, (start_date,))
        conn.commit()

        offset_days = 0 #表示quizlet set的日期比当前日期多几天
        #以下大循环，每运转一圈，则quizlet set的日期往后走一天，知道所有的记忆记录都规划了时间
        while True:
            #单词记忆计划表中的每一条记忆记录都规划了时间的情况下，就可以退出这个循环了
            cursor.execute("SELECT count(1) FROM word_remember_plan WHERE plan_status='UNPLANNED'")
            if cursor.fetchone()[0] == 0:
                break

            #获取quizlet set使用的日期，这个日期在制定计划的过程中会用到，也会在quizlet set的导出文件中名中会用到
            sql = "select strftime('%Y%m%d', date(?, ?) ), strftime('%Y-%m-%d', date(?, ?) )"
            cursor.execute(sql, (start_date, '+{} day'.format(offset_days), start_date, '+{} day'.format(offset_days), ))
            row = cursor.fetchone()
            cmp_date_str = row[0] #YYYYMMDD格式的日期字符串
            date_str = row[1] #YYYY-MM-DD格式的日期字符串

            #当天的quizlet set中的词汇
            quizlet_set = set()

            # 针对记忆计划已经被开启了的词汇（也就是seq=0的记录的plan_remember_date已经在此前被确定了的词汇，
            # 无论word_type取值是什么，这些词汇在quizlet set中都算是旧词）
            # seq_no从后往前找，看是否存在已经到期需要复习的旧词
            for seq_no in range(4, 0, -1):
                sql="select word, julianday(date(?))-julianday(date(plan_remember_date, '+'||gap_days||' day')) delay_days " \
                    "from word_remember_plan where plan_status='PLANNED' " \
                    "and date(plan_remember_date, '+'||gap_days||' day') <= date(?) and seq_no=? " \
                    "and word in (select word from word_remember_plan where seq_no=? " \
                    "and plan_status='UNPLANNED' ) order by delay_days desc"
                cursor.execute(sql, (date_str, date_str, seq_no - 1, seq_no, ))

                words = set()
                for row in cursor:
                    if len(quizlet_set) + len(words) >= old_word_cnt:
                        break #如果旧词的量已经达到了，就不要再添加旧词了
                    words.add(row[0])
                quizlet_set = quizlet_set | words
                for word in words:
                    sql = "update word_remember_plan set plan_status='PLANNED', " \
                          "plan_remember_date=date(?) where word=? and seq_no=?"
                    cursor.execute(sql, (date_str, word, seq_no,))
                    conn.commit()

            #启动还没有开始复习的旧词
            sql="select word from word_remember_plan where word_type='OLD' and " \
                "plan_status='UNPLANNED' and seq_no=0 "
            cursor.execute(sql)
            words = set()
            for row in cursor:
                if len(quizlet_set) + len(words) >= old_word_cnt:
                    break #如果旧词的量已经达到了，就不要再添加旧词了
                words.add(row[0])
            quizlet_set = quizlet_set | words
            for word in words:
                sql = "update word_remember_plan set plan_status='PLANNED', " \
                      "plan_remember_date=date(?), ideal_remember_date=date(?) where word=? and seq_no=0"
                cursor.execute(sql, (date_str, date_str, word,))
                conn.commit()
                #把这个单词的其它记忆点的理想时间设置上去
                sum_gap_days = 0
                for ideal_seq in range(0, 4):
                    sql = "select gap_days from word_remember_plan where word=? and seq_no=?"
                    cursor.execute(sql, (word, ideal_seq, ))
                    row = cursor.fetchone()
                    if row == None:
                        break
                    sum_gap_days += row[0]
                    sql = "update word_remember_plan set ideal_remember_date=date(?, '+'||?||' day') where word=? and seq_no=?"
                    cursor.execute(sql, (date_str, sum_gap_days, word, ideal_seq+1, ))
                    conn.commit()

            #启动还没有开始记忆的新词
            sql="select word from word_remember_plan where word_type='NEW' and " \
                "plan_status='UNPLANNED' and seq_no=0 "
            cursor.execute(sql)
            words = set()
            for row in cursor:
                if len(words) >= set_size - len(quizlet_set):
                    break #如果新词的量已经达到了，就不要再添加新词了
                words.add(row[0])
            quizlet_set = quizlet_set | words
            for word in words:
                sql = "update word_remember_plan set plan_status='PLANNED', " \
                      "plan_remember_date=date(?), ideal_remember_date=date(?) where word=? and seq_no=0"
                cursor.execute(sql, (date_str, date_str, word,))
                conn.commit()
                #把这个单词的其它记忆点的理想时间设置上去
                sum_gap_days = 0
                for ideal_seq in range(0, 4):
                    sql = "select gap_days from word_remember_plan where word=? and seq_no=?"
                    cursor.execute(sql, (word, ideal_seq, ))
                    row = cursor.fetchone()
                    if row == None:
                        break
                    sum_gap_days += row[0]
                    sql = "update word_remember_plan set ideal_remember_date=date(?, '+'||?||' day') where word=? and seq_no=?"
                    cursor.execute(sql, (date_str, sum_gap_days, word, ideal_seq+1, ))
                    conn.commit()

            #把quizlet set写入到文件中
            dictcn = dict_cn()
            words = {}
            for word in quizlet_set:
                dict_word, meaning = dictcn.search(word)
                words[dict_word] = meaning
            self.__write_dict_to_file(words, "words/plan/remember-{}.txt".format(cmp_date_str))

            #做下一天的quizlet set
            offset_days += 1

        conn.close()

    def __print_word_list(self, list):
        for word in list:
            print(word)
