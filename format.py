#-*-coding:utf-8 -*-

import csv
import re
import sys
import random

# # 将文件转换为csv格式
# def changeToCSV(oldPath,newPath,spl):
#     with open(newPath, 'w+', newline='', encoding='utf-8') as csvfile:
#         spamwriter = csv.writer(csvfile, dialect='excel')  # dialect可用delimiter= ','代替，后面的值是自己想要的符号
#         # 读要转换的文件，文件每行各词间以' # '字符分隔
#         # spamwriter.writerow(['user_name','password','email'])
#         with open(oldPath, 'r', encoding='utf-8', errors="ignore") as filein:
#             for line in filein:
#                 line_list = line.strip('\n').split(spl)
#                 spamwriter.writerow(line_list)

# 将csv口令提取出来，生成测试集和训练集两个文件
def readFile(path,seed,eps):
    passwd = []
    n = 0
    try:
        file = open(path, 'r', errors="ignore")
        lines = file.readlines()
        for line in lines:
            if n < 2:
                pass
            else:
                if len(line.split(":")) == 3:
                    _,_,pwd = line.split(":")
                passwd.append(pwd)
            n += 1
    except FileNotFoundError:
        print("The password file does not exist", file=sys.stderr)
    file.close()


    # 切分数据集（训练集和测试集）
    random.seed(seed)#每次生成随机数一样，测试集40%
    l = random.sample(range(0, len(passwd)), int(len(passwd) * eps))#sample(list, k)返回一个长度为k新列表，新列表存放list所产生k个随机唯一的元素
    testword = [passwd[i] for i in l]

    trainword = []
    for i in range(0,len(passwd)):
        if i not in l:
            print(i) #控制台查看生成结果
            trainword.append(passwd[i])

    with open("trainword.txt", "w") as f:
        for pd in trainword:
            f.write(pd)

    with open("testword.txt", "w") as f:
        for pd in testword:
            f.write(pd)

# 将csv口令提取出来，生成测试集和训练集两个文件
def readFile2(path,seed,eps):
    passwd = []
    n = 0
    try:
        file = open(path, 'r', encoding='ISO-8859-1', errors="ignore")
        lines = file.readlines()
        for line in lines:
            if n < 2:
                pass
            else:
                if len(line.split("#")) == 3:
                    _,pwd,_ = line.split("#")
                passwd.append(pwd)
            n += 1
    except FileNotFoundError:
        print("The password file does not exist", file=sys.stderr)
    file.close()


    # 切分数据集（训练集和测试集）
    random.seed(seed)#每次生成随机数一样，测试集40%
    l = random.sample(range(0, len(passwd)), int(len(passwd) * eps))#sample(list, k)返回一个长度为k新列表，新列表存放list所产生k个随机唯一的元素
    testword = [passwd[i] for i in l]

    trainword = []
    for i in range(0,len(passwd)):
        if i not in l:
            print(i) #控制台查看生成结果
            trainword.append(passwd[i])

    with open("trainword.txt", "w", errors="ignore") as f:
        for pd in trainword:
            f.write(pd+'\n')

    with open("testword.txt", "w") as f:
        for pd in testword:
            f.write(pd+'\n')

if __name__ == '__main__':
     # changeToCSV('www.csdn.net.sql','csdn.csv',' # ')
     # changeToCSV('plaintxt_yahoo.txt','yahoo.csv',':')
     # readFile('yahoo.csv',2,0,0.4)
     readFile2('www.csdn.net.sql', 0, 0)