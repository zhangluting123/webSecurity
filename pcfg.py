# @Author: zlt
# @Time  : 2021/10/20 
# @File  : pcfg
# @Description: PCFG格式解析实现
'''
假设前提已有testword.txt和trainword.txt文件，里面分别存放单列测试口令和训练口令【format.py】
'''
import os
import re

Lp = re.compile('L')#字母
Dp = re.compile('D')
Sp = re.compile('S')

# 读取数据集
def loadpass(path):
    passwd = []
    with open(path, encoding='utf-8', errors='ignore') as wordList:
        for line in wordList:
            passwd.append(line.strip())
    return passwd

# 统计基本结构以及字段出现的次数
'''
#part:5678 asf 1234 #@ 5678 .. 78 abc 
#m :D4 L3 D4 S2 D4 S2 D2 L3
#model= {'D4L3D4S2D4S2D2L3': 1}
#alpha = {'L3':{'asf':1,'abc':1}}
#digit = {'D4':{'5678': 2, '1234': 1},'D2':{'78':1}}
#special = {'S2':{'#@':1,'..':1}}
'''
def count(part, m, a):

    if m in a:
        if part in a[m]:
            a[m][part] += 1
        else:
            a[m].setdefault(part, 1)
    else:
        a.setdefault(m, {})
        a[m].setdefault(part, 1)

# 将字母、数字、特殊字符次数转化为频率
'''
{'L3':{'asf':0.5,'abc':0.5}}
{'D4': {'5678': 0.66,'1234': 0.33}, 'D2': {'78': 1}}
'''
def probability(d):
    for key in d.keys():
        num = sum(d[key].values())
        for k in d[key].keys():
            d[key][k] = d[key][k]*1.0 / num

# 将结构出现次数转化为频率
'''{'L3D4S3':0.25,'D4L3D4S2D4S2D2L3':0.75}'''
def base_probability(d):
    num = sum(d.values())
    for key in d.keys():
        d[key] = d[key] * 1.0 / num

# 口令切割统计
def statistic(trainword):

    mode = {} #存放基础结构LDS及次数
    alpha = {}
    digit = {}
    special = {}

    pattern = re.compile(r'[A-Za-z]*|[0-9]*|[^a-zA-Z0-9]*', re.ASCII)
    for pd in trainword:
        s = ''
        parts = re.findall(pattern, pd)
        for part in parts:
            if part == '':
                continue
            else:
                l = len(part)
                if part.isdigit():
                    m = 'D'+str(l)
                    count(part, m, digit)
                elif part.isalpha():
                    m = 'L'+str(l)
                    count(part, m, alpha)
                else:
                    m = 'S'+str(l)
                    count(part, m, special)
            s += m  #结构格式
        if s in mode:
            mode[s] += 1
        else:
            mode.setdefault(s, 1)
    return mode, alpha, digit, special

# 生成结构
def create_base_struct(base, alpha, digit, special):
    #当前路径下生成struct目录
    if(not os.path.exists('base_struct')):
        os.mkdir('base_struct')
    if(not os.path.exists('base_alpha')):
        os.mkdir('base_alpha')
    if(not os.path.exists('base_digit')):
        os.mkdir('base_digit')
    if(not os.path.exists('base_special')):
        os.mkdir('base_special')

    print('=====正在写入基础结构====')
    filepath = './base_struct/base_struct.txt'
    with open(filepath, mode='a+') as f:
        for s in base:
            f.write(s[0] + '\t'+ str(s[1]) + '\n')
    print('=====基础结构写入完毕====')

    print('======正在写入字母======')
    for key,value in alpha.items():
        filepath = './base_alpha/' + key + '.txt'
        with open(filepath, mode='a+') as f:
            for p in value:
                f.write(p[0] + '\t' + str(p[1]) + '\n')
    print('=====字母写入完毕=======')

    print('======正在写入数字======')
    for key,value in digit.items():
        filepath = './base_digit/' + key + '.txt'
        with open(filepath, mode='a+') as f:
            for p in value:
                f.write(p[0] + '\t' + str(p[1]) + '\n')
    print('=====数字写入完毕=======')

    print('=====正在写入特殊字符====')
    for key,value in special.items():
        filepath = './base_special/' + key + '.txt'
        with open(filepath, mode='a+') as f:
            for p in value:
                f.write(p[0] + '\t' + str(p[1]) + '\n')
    print('=====特殊字符写入完毕=====')

if __name__ == '__main__':
    #导入训练集
    trainword = loadpass('trainword.txt')
    #口令切割统计
    oribase, orialpha, oridigit, orispecial = statistic(trainword)
    #将基础结构出现次数转化为频率
    base_probability(oribase)
    #将字母、数字、特殊字符出现次数转化为频率
    probability(orialpha)
    probability(oridigit)
    probability(orispecial)
    #基础结构频率排序（由高到低）
    oribase = sorted(oribase.items(), key=lambda t: t[1], reverse=True)
    #字母频率排序
    for key, value in orialpha.items():
        orialpha[key] = sorted(value.items(), key=lambda t: t[1], reverse=True)
    #数字频率排序
    for key, value in oridigit.items():
        oridigit[key] = sorted(value.items(), key=lambda t: t[1], reverse=True)
    #特殊字符频率排序
    for key, value in orispecial.items():
        orispecial[key] = sorted(value.items(), key=lambda t: t[1], reverse=True)
    #写入指定文件
    create_base_struct(oribase ,orialpha, oridigit, orispecial)
    # print(oribase)
    # print(orialpha)
    # print(oridigit)
    # print(orispecial)