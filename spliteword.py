import requests
from ciba import Ciba
from rememberedwords import RememberedWords

class WordSpliter():
    def __init__(self):
        self.rememberedWords = RememberedWords()

    def isNewWord(self, segment):
        #print('=='+segment)

        #除掉空格长度为零
        if (len(segment.strip())==0):
            return False

        #包含了非字母字符
        for i in range(0, len(segment)):
            #print(segment[i])
            if not (segment[i] >= 'a' and segment[i] <= 'z' or segment[i] >= 'A' and segment[i] <= 'Z'):
                return False

        #曾经记忆过的单词
        if self.rememberedWords.isRemember(segment):
            return False

        ciba = Ciba()
        result = ciba.searchInCiba(segment)

        #排除不存在的单词
        if result == None:
            print('不存在的单词={}'.format(segment))
            return False

        #排除人名
        if result.find('女子名') != -1 or result.find('男子名') != -1:
            #print('人名={}'.format(segment))
            return False

        return True

    def splitList(self, list, divided):
        result = []
        for line in list:
            splited = line.split(divided)
            result.extend(splited)
        return result

    def roughSplit(self, line):
        result = []

        result.append(line)
        result = self.splitList(result, ' ')
        result = self.splitList(result, '\t')
        result = self.splitList(result, '\n')
        result = self.splitList(result, '\r')
        result = self.splitList(result, '.')
        result = self.splitList(result, ',')
        result = self.splitList(result, '!')
        result = self.splitList(result, '"')

        return result

    def spliteword(self, file):
        wordset = set()
        newwordset = set()
        for line in open(file):
            roughWordList = self.roughSplit(line)
            for word in roughWordList:
                word = word.lower()
                word = word.strip('\n')
                word = word.strip('\r')
                word = word.strip('\t')
                if word in wordset :
                    continue
                wordset.add(word)
                if self.isNewWord(word):
                    newwordset.add(word)
                    print('[{}]={}'.format(len(newwordset), word))
                    with open("words/newword.txt", 'a') as f:
                        f.write(word + '\n')

if __name__ == '__main__':
    spliter = WordSpliter()
    spliter.spliteword('words/article.txt')

