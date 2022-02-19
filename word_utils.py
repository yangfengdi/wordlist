from word_set import word_set
from db_utils import db_utils

#初始化数据库的过程中导入的数据
def db_init_import(utils):
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
    #utils.import_word_tag('words/archive/tag-六级.txt', '六级')
    #utils.import_word_tag('words/archive/tag-托福.txt', '托福')

    #导入单词错词本
    #utils.import_quiz_fail_event('words/fail-20210201.txt', '2021-02-01')

    pass

#显示单词统计信息
def show_stat_info(word_set):
    #数据统计
    remembered_words = word_set.words_min_remember_times()
    print('背过的单词总数={}'.format(len(remembered_words)))

    passed_words = word_set.words_last_quiz_pass()
    print('测验通过的单词总数={}'.format(len(passed_words)))

    words = word_set.words_with_tag('俞敏洪初中')
    print('初中词汇:\t\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                        round(len(words & remembered_words) * 100 / len(words)),
                                                        len(words & passed_words),
                                                        round(len(words & passed_words) * 100 / len(words))))

    words = word_set.words_with_tag('俞敏洪高中')
    print('高中词汇:\t\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                        round(len(words & remembered_words) * 100 / len(words)),
                                                        len(words & passed_words),
                                                        round(len(words & passed_words) * 100 / len(words))))

    words = word_set.words_with_tag('俞敏洪四级')
    print('四级词汇:\t\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                        round(len(words & remembered_words) * 100 / len(words)),
                                                        len(words & passed_words),
                                                        round(len(words & passed_words) * 100 / len(words))))

    words = word_set.words_with_tag('六级')
    print('六级词汇:\t\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                        round(len(words & remembered_words) * 100 / len(words)),
                                                        len(words & passed_words),
                                                        round(len(words & passed_words) * 100 / len(words))))

    words = word_set.words_with_tag('托福')
    print('托福词汇:\t\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                        round(len(words & remembered_words) * 100 / len(words)),
                                                        len(words & passed_words),
                                                        round(len(words & passed_words) * 100 / len(words))))

    words = word_set.word_by_freq('AE', 0, 5000)
    #print('{}'.format(len(ae5000)))
    print('美语TOP5000:\t\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                             round(len(words & remembered_words) * 100 / len(words)),
                                                             len(words & passed_words),
                                                             round(len(words & passed_words) * 100 / len(words))))

    words = word_set.word_by_freq('AE', 0, 10000)
    #print('{}'.format(len(ae5000)))
    print('美语TOP10000:\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                             round(len(words & remembered_words) * 100 / len(words)),
                                                             len(words & passed_words),
                                                             round(len(words & passed_words) * 100 / len(words))))

    words = word_set.word_by_freq('AE', 0, 15000)
    #print('{}'.format(len(ae5000)))
    print('美语TOP15000:\t总量={};\t背过={}({}%);\t测验通过={}({}%)'.format(len(words), len(words & remembered_words),
                                                                  round(len(words & remembered_words) * 100 / len(words)),
                                                                  len(words & passed_words),
                                                                  round(len(words & passed_words) * 100 / len(words))))


    #recent_quiz_words= word_set.words_recent_quiz(30)
    #print('30天内做过测验的单词数：{}'.format(len(recent_quiz_words)))

if __name__ == '__main__':
    word_set = word_set()
    show_stat_info(word_set) #展示单词统计信息

    utils = db_utils()

    #导入单词记忆事件
    utils.import_remember_events('words/remember')

    #导入单词测验结果
    utils.import_quiz_result('words/quiz')

    #制作测试题
    #word_set.make_quiz_from_fail_record('2022-02-18', 8)
    #word_set.make_quiz_from_remembered_some_days_words('2022-02-18', 8)
    #word_set.make_quiz_from_tag('俞敏洪初中', '2022-02-18', 8)

    #创建新词列表
    #word_set.get_new_words_from_articles('words/article')
    #word_set.get_new_words_from_docxs('words/docx')
    #word_set.get_new_words_from_list('words/words.txt')
    #word_set.get_new_words_from_top_freq()

    #创建待记忆词汇记忆模板，这些词汇将会适时被排入quizlet set中
    #utils.import_word_remember_plan('words/newword.txt', 'NEW', (1, 2, 3, 8, 0))
    #utils.import_word_remember_plan('words/review.txt', 'OLD', (2, 3, 8, 0))
    #word_set.create_quizlet_set('2022-02-20', 75, 12)

    #创建复习quizlet列表
    #word_set.get_words_from_recent_remember_words()
    #word_set.get_review_words_from_fail_record()
    #word_set.get_words_from_tag('俞敏洪初中')

    #把多个不同的单词列表混合成一个大quizlet列表
    #word_set.get_new_words_from_list_without_filter('words/words.txt')

    #从文章中把单词抽取出来（不过滤）
    #word_set.get_words_from_article('words/tf.txt')

