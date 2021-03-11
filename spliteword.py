import requests
from ciba import Ciba
from rememberedwords import RememberedWords

class Word():
    def __init__(self):
        self.word = ''
        self.meaning = ''
        self.isWord = False
        self.isNewWord = False
        self.isName = False
        self.isAbbr = False
        self.isVariant = False  #这个词是不是个变体，如：复数，过去分词，过去式等

class WordSpliter():
    def __init__(self):
        self.rememberedWords = RememberedWords()

    def analyseWord(self, segment):
        word = Word()
        word.word = segment
        #print('=='+segment)

        #除掉空格长度为零或者为1的单词不算
        if (len(segment.strip())<2):
            return word

        #包含了非字母字符
        for i in range(0, len(segment)):
            #print(segment[i])
            if not (segment[i] >= 'a' and segment[i] <= 'z' or segment[i] >= 'A' and segment[i] <= 'Z'):
                return word

        #曾经记忆过的单词
        if self.rememberedWords.isRemember(segment):
            word.isNewWord = False
            return word

        word.isNewWord = True

        ciba = Ciba()
        result = ciba.searchInCiba(segment)

        #排除不存在的单词
        if result == None:
            print('不存在的单词={}'.format(segment))
            word.isWord = False
            return word

        #这样写有点丑，先这么写着，以便兼容之前的程序
        word.word = result[:result.find("|")]
        word.meaning = result[result.find("|")+1:]

        if len(word.word) >= 2:
            word.isWord = True

        if result.find('女子名') != -1 or result.find('男子名') != -1:
            word.isName = True

        if result.find('abbr.') != -1:
            word.isAbbr = True

        if result.find('的现在分词') != -1:
            word.isVariant = True

        if result.find('的过去式') != -1:
            word.isVariant = True

        if result.find('的过去分词') != -1:
            word.isVariant = True

        if result.find('的过去式和过去分词') != -1:
            word.isVariant = True

        if result.find('的名词复数') != -1:
            word.isVariant = True

        if result.find('的复数形式') != -1:
            word.isVariant = True

        if result.find('的第三人称单数') != -1:
            word.isVariant = True

        if result.find('的比较级') != -1:
            word.isVariant = True

        if result.find('的最高级') != -1:
            word.isVariant = True

        return word

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
            for roughWord in roughWordList:
                roughWord = roughWord.lower()
                roughWord = roughWord.strip('\n')
                roughWord = roughWord.strip('\r')
                roughWord = roughWord.strip('\t')
                if roughWord in wordset :
                    continue
                wordset.add(roughWord)
                word = self.analyseWord(roughWord)

                if not word.isWord:
                    continue

                #跳过人名
                if word.isName:
                    continue

                #跳过缩写词
                if word.isAbbr:
                    continue

                #跳过变体词
                if word.isVariant:
                    continue

                if word.isNewWord:
                    newwordset.add(word.word)
                    print('[{}]={}'.format(len(newwordset), word.word))
                    with open("words/newword.txt", 'a') as f:
                        f.write('{}|{}'.format(word.word, word.meaning) + '\n')


if __name__ == '__main__':
    spliter = WordSpliter()
    spliter.spliteword('words/article.txt')

