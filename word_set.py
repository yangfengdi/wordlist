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

        words = words - self.words_min_remember_times(1) #如果一个词曾经被背过一定次数以上就跳过
        words = words - self.words_last_quiz_pass() #如果一个词最近一次测验是通过的就跳过
        words_dict = self.__filter_words(words)
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

        words = words - self.words_min_remember_times(1) #如果一个词曾经被背过一定次数以上就跳过
        words = words - self.words_last_quiz_pass() #如果一个词最近一次测验是通过的就跳过
        words_dict = self.__filter_words(words)
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

        words_top_freq = self.word_by_freq('BE', 0, 20000)|self.word_by_freq('AE', 0, 20000)

        words_list = words_list - words_except #去除某些简单单词，如小学、初中单词等
        words_list = words_list - words_variant  #去除变体的单词
        words_list = words_list - words_proper #去除专用单词，如：国名、地名、人名等
        words_list = words_list - words_first_letter_capital #去除首字母大写单词

        result = {}
        for word in words_list: #不筛除低频词
        #for word in words_in_artical&words_top_freq:  #筛除低频词
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

    def make_quiz_from_fail_record(self, quiz_tag, page_max = 10):
        words = self.words_last_quiz_fail()
        words = words - self.words_max_last_remember_days(15) #最近15天内背过的单词不测验
        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        self.__make_quiz(words, quiz_tag, page_max)

    def make_quiz_from_tag(self, words_tag, quiz_tag, page_max = 10):
        words = self.words_with_tag(words_tag)
        words = words - self.words_max_last_remember_days(15) #最近15天内背过的单词不测验
        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        self.__make_quiz(words, quiz_tag, page_max)

    def make_quiz_from_remembered_some_days_words(self, quiz_tag, page_max=10):
        words = self.words_min_remember_times(3) #至少背过3次的单词
        words = words & self.words_min_last_remember_days(30) #最近一次记忆是在30天以前
        words = words - self.words_last_quiz_pass() #最近一次测验是通过的单词不测验
        words = words - self.words_recent_quiz(30) #最近30天内做过测验的单词不测验
        self.__make_quiz(words, quiz_tag, page_max)

    def __make_quiz(self, words, quiz_tag, page_max = 10):
        words_list = set()
        words_meaning = {}

        dictcn = dict_cn()
        for word in words:
            dict_word, meaning = dictcn.search(word)
            words_meaning[dict_word] = meaning
            words_list.add(dict_word)

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

        words_list = words_list - words_variant  #去除变体的单词
        words_list = words_list - words_proper #去除专用单词，如：国名、地名、人名等
        words_list = words_list - words_first_letter_capital #去除首字母大写单词

        words_dict = {}
        for word in words_list:
            words_dict[word] = words_meaning[word]

        pdf_filename = "words/quiz-{}.pdf".format(quiz_tag)
        txt_filename = "words/quiz-{}.txt".format(quiz_tag)

        chinese_number = ['0', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
        roman_number = ['0', 'Ⅰ.', 'Ⅱ.', 'Ⅲ.', 'Ⅳ.', 'Ⅴ.', 'Ⅵ.', 'Ⅶ.', 'Ⅷ.', 'Ⅸ.', 'Ⅹ.']
        canv = canvas.Canvas(pdf_filename)
        pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))

        words_per_page = 6
        quiz_words = {}
        quiz_meanings = {}
        quiz_meanings_disorder = {}
        inside_page_index = 0
        page_no = 0
        for word in words_dict.keys():
            if inside_page_index == words_per_page:
                inside_page_index = 0
                page_no += 1

                style = ParagraphStyle(name='normal')
                style.fontSize = 20
                style.fontName = "SimSun"
                style.alignment = 1
                p = Paragraph("{}-单词练习-{}".format(quiz_tag, page_no), style)
                p.wrap(210 * mm, 35 * mm)
                p.drawOn(canv, 0, 292 * mm)

                with open(txt_filename, 'a') as f:
                    f.write('##Page-{}'.format(page_no) + '\n')

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

            if page_no >= page_max:
                break

            quiz_words[inside_page_index] = word
            quiz_meanings[inside_page_index] = words_dict[word]
            inside_page_index += 1

        canv.save()

