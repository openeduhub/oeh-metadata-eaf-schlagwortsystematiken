from striprtf.striprtf import rtf_to_text
from os import listdir
from os.path import isfile, join

files = [f for f in listdir('data/rtf') if isfile(join('data/rtf', f))]

for _file in files:
    print(f'file is {_file}')
    rtf = open('data/rtf/' + _file).read()
    text = rtf_to_text(rtf)
    filename = 'data/txt/' + _file.split('.')[0] + '.txt'
    with open(filename, "w") as f:
        f.write(text)
        f.close()
