import requests
from ciba import Ciba
from dictcn import Dictcn
from rememberedwords import RememberedWords
from word import Word
import random

class WordSpliter():
    def __init__(self):
        self.rememberedWords = RememberedWords()
        self.skipRemember = True
        self.randomOrder = False

    def analyseWord(self, segment):
        word = Word()
        word.word = segment
        #print('=='+segment)

        #除掉空格长度为零或者为1的单词不算
        if (len(segment.strip())<2):
            #print('{}长度太短'.format(segment))
            return word

        #包含了不合法字符（非字母、非空格，非连字符）
        for i in range(0, len(segment)):
            #print(segment[i])
            if not (segment[i] >= 'a' and segment[i] <= 'z'
                    or segment[i] >= 'A' and segment[i] <= 'Z'
                    or segment[i]==' '
                    or segment[i]=='\''
                    or segment[i]=='-'):
                #print('包含非法字符={}'.format(segment))
                return word

        #曾经记忆过的单词
        if self.rememberedWords.isRemember(segment):
            word.isRemember = True
        else:
            word.isRemember = False

        #dict = Ciba()
        dict = Dictcn()
        result = dict.search(segment)

        #排除不存在的单词
        if result == None:
            print('不存在的单词={}'.format(segment))
            word.isWord = False
            return word

        word.isWord = True

        #这样写有点丑，先这么写着，以便兼容之前的程序
        word.word = result[:result.find("|")]
        word.meaning = result[result.find("|")+1:]

        if result.find('女子名') != -1 or result.find('男子名') != -1 or result.find('人名') != -1:
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

        if result.find('的ing形式') != -1:
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

        #如果包含词组，则不能用空格作为分割的依据
        #针对词组，需要提前对文章进行预处理，一般以换行作为分割的依据
        result = self.splitList(result, ' ')

        result = self.splitList(result, '\t')
        result = self.splitList(result, '\n')
        result = self.splitList(result, '\r')
        result = self.splitList(result, '/')
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
                #roughWord = roughWord.lower()
                roughWord = roughWord.strip(' ')
                roughWord = roughWord.strip('\n')
                roughWord = roughWord.strip('\r')
                roughWord = roughWord.strip('\t')

                if roughWord in wordset :
                    #print('skip word 1 = {}'.format(roughWord))
                    continue

                wordset.add(roughWord)

                word = self.analyseWord(roughWord)

                if self.skipRemember:
                    if self.rememberedWords.isRemember(word.word):
                        continue

                if len(word.word) == 0:
                    #print('skip word 2 = {}'.format(roughWord))
                    continue

                if not word.isWord:
                    #print('skip word 2 = {}'.format(roughWord))
                    continue

                #跳过人名
                if word.isName:
                    #print('跳过人名')
                    continue

                #跳过缩写词
                if word.isAbbr:
                    continue

                #跳过变体词
                if word.isVariant:
                    continue

                newwordset.add(word.word)
                print('[{}]={}'.format(len(newwordset), word.word))
                with open("words/newword.txt", 'a') as f:
                    f.write('{}|{}'.format(word.word, word.meaning) + '\n')
                    #f.write('{}'.format(word.word) + '\n')

    def buildSet(self, file):
        wordSpellSet = set()
        wordList = list()
        for line in open(file):
            line = line.strip('\n')
            #line = line.strip(' ')
            word = Word()

            # 这样写有点丑，先这么写着，以便兼容之前的程序
            if line.find("|") == -1:
                word.word = line
            else:
                word.word = line[:line.find("|")]
                word.meaning = line[line.find("|") + 1:]

            if word.word in wordSpellSet :
                print('skip duplicated word {}.'.format(word.word))
                continue

            if self.skipRemember:
                if self.rememberedWords.isRemember(word.word):
                    print('skip remembered word {}.'.format(word.word))
                    continue

            if len(word.meaning) ==0:
                #print('search {}'.format(word.word))
                word = self.analyseWord(word.word)

            if len(word.word) == 0:
                print('skip empty word {}.'.format(word.word))
                continue

            wordSpellSet.add(word.word)
            wordList.append(word)

        if self.randomOrder:
            # 刻意打乱顺序输出到文件
            while len(wordList) > 0:
                randIndex = random.randint(0, len(wordList) - 1)
                worditem = wordList[randIndex]
                with open("words/result.txt", 'a') as f:
                    f.write('{}|{}'.format(worditem.word, worditem.meaning) + '\n')
                del wordList[randIndex]
        else:
            # 按照原来的顺序输出到文件
            for worditem in wordList:
                with open("words/result.txt", 'a') as f:
                    f.write('{}|{}'.format(worditem.word, worditem.meaning) + '\n')
                    # f.write('{}'.format(word.word) + '\n')


if __name__ == '__main__':
    spliter = WordSpliter()

    spliter.skipRemember = True
    #spliter.skipRemember = False

    #spliter.randomOrder = True
    spliter.randomOrder = False

    spliter.spliteword('words/article.txt')
    #spliter.spliteword('words/englishname.txt')
    #spliter.buildSet('words/words.txt')

