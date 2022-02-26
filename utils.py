import os

def batch_rename_file(dir):
    dirs = os.listdir( dir )
    file_no = 0
    for subdir in dirs:
        if os.path.isdir('{}/{}'.format(dir, subdir)):
            files = os.listdir('{}/{}'.format(dir, subdir))
            for file in files:
                if not os.path.isfile('{}/{}/{}'.format(dir, subdir, file)):
                    continue
                if file.endswith('.jpg'):
                    file_no += 1
                    #print('{}/{}/{} ==> {}/{}.jpg'.format(dir, subdir, file, dir, file_no))
                    os.rename('{}/{}/{}'.format(dir, subdir, file), '{}/{}.jpg'.format(dir, file_no))

if __name__ == '__main__':
    batch_rename_file('/Users/Allan/Desktop/RAZ/tmp/K')

