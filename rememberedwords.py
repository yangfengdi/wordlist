import os
import sqlite3

class RememberedWords():
    def __init__(self):
        self.wordset = set()
        #self.__loadWords()
        self.__loadWordsFromDb()
        print('Remembered word count = {}'.format(len(self.wordset)))

    def __loadWordsFromDb(self):
        conn = sqlite3.connect('dict.db')
        cursor = conn.cursor()

        cursor.execute("SELECT distinct word FROM remember_event")
        #cursor.execute("select distinct a.word from remember_event a, word_tag b where a.word=b.word and b.tag in ('小学','俞敏洪初中','简单词')")
        rows = cursor.fetchall()
        for row in rows:
            #print(row[0])
            self.wordset.add(row[0])

        conn.close()

    def __loadWords(self):
        fileList = os.listdir('words')
        for file in fileList:
            if file.startswith('remember') and file.endswith('.txt'):
                self.__loadWordsFromFile('words/{}'.format(file))

    def __loadWordsFromFile(self, filename):
        for line in open(filename):
            line = line.strip('\n')
            line = line.strip('\r')
            dividePos = line.find('|')
            if dividePos == -1:
                word = line
            else:
                word = line[:dividePos]
            #print('word={}'.format(word))
            self.wordset.add(word)

    def isRemember(self, word):
        return word in self.wordset
