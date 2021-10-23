#-*-coding:utf-8 -*-
# @Author: zlt
# @Time  : 2021/10/20 
# @File  : format
# @Description: 文件格式转换
import csv
import re
import sys
import random

# 将文件转换为csv格式
def changeToCSV(oldPath,newPath,spl):
    with open(newPath, 'w+', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, dialect='excel')  
        # 读要转换的文件，文件每行各词间以' # '字符分隔
        # spamwriter.writerow(['user_name','password','email'])
        with open(oldPath, 'r', encoding='utf-8', errors="ignore") as filein:
            for line in filein:
                line_list = line.strip('\n').split(spl)
                spamwriter.writerow(line_list)

# 将csv口令提取出来，生成测试集和训练集两个文件
def readFile(path,col,seed,eps):
    passwd = []
    exp = re.compile(r'[^\x00-\x7f]')
    try:
        with open(path, encoding='utf-8') as wordlist:
            for line in wordlist:
                wl = line.strip().split(',')#split(分隔符,num)分割成num+1个子串
                if(len(wl)<3): #有一行错误码要剔除
                    continue
                pd = wl[col]
                if exp.search(pd) or ' ' in pd: # 过滤非ASCLL字符和空格
                    continue
                else:
                    passwd.append(pd)
    except FileNotFoundError:
        print("The password file does not exist", file=sys.stderr)

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
            f.write(pd + '\n')

    with open("testword.txt", "w") as f:
        for pd in testword:
            f.write(pd + '\n')

if __name__ == '__main__':
    # changeToCSV('www.csdn.net.sql','csdn.csv',' # ')
    # changeToCSV('plaintxt_yahoo.txt','yahoo.csv',':')
    readFile('yahoo.csv',2,0,0.4)