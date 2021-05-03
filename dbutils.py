import sqlite3

class dbutils():

    def import_dict(self, file, source):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

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
                print('skip duplicated word {}.'.format(word))
                continue

            cursor.execute("INSERT INTO dict (word, meaning, source) VALUES ('{}', '{}', '{}')".format(word, meaning, source))
            conn.commit()

        conn.close()

    def import_word_tag(self, file, tag):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

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
                print('skip duplicated tag, word={} tag={}.'.format(word, tag))
                continue

            cursor.execute("INSERT INTO word_tag (word, tag) VALUES ('{}', '{}')".format(word, tag))
            conn.commit()

        conn.close()


if __name__ == '__main__':
    utils = dbutils()

    #导入自定义的单词，多数是来自课堂笔记，一般是有特定意义的单词，如：MAP Math单词
    utils.import_dict('words/dict-MAP.txt', 'MAP')

    #导入单词标签，即单词的分类
    utils.import_word_tag('words/tag-俞敏洪高中.txt', '俞敏洪高中')

