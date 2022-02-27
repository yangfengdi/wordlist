import os

#用于批量处理RAZ书籍的jpg的工具
def batch_rename_file(dir):
    dirs = os.listdir( dir )
    file_no = 0
    os.mkdir('{}/000000'.format(dir))
    for subdir in dirs:
        if os.path.isdir('{}/{}'.format(dir, subdir)):
            files = os.listdir('{}/{}'.format(dir, subdir))
            for file in files:
                if not os.path.isfile('{}/{}/{}'.format(dir, subdir, file)):
                    continue
                if file == '01.jpg' or file == '02.jpg':  #跳过每本书的前两页，没有有价值的信息
                    continue
                if file.endswith('.jpg'):
                    file_no += 1
                    print('{}/{}/{} ==> {}/000000/{}.jpg'.format(dir, subdir, file, dir, file_no))
                    os.rename('{}/{}/{}'.format(dir, subdir, file), '{}/000000/{}.jpg'.format(dir, file_no))

if __name__ == '__main__':
    batch_rename_file('/Users/Allan/Desktop/RAZ/TMP-L/L')

