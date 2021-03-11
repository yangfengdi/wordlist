import os

class RememberedWords():
    def __init__(self):
        self.wordset = set()
        self.__loadWords()
        print('Remembered word count = {}'.format(len(self.wordset)))

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
