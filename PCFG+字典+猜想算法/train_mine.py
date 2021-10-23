import re
import random
import sys


# 读取数据集
def loadpass(path):

    passwd = []
    with open(path, encoding='utf-8', errors='ignore') as wordList:
        for line in wordList:
            passwd.append(line.strip())
    return passwd

# 统计每种结构以及字段出现的次数
'''
#part:5678 asf 1234 #@ 5678 .. 78 abc 
#m :D4 L3 D4 S2 D4 S2 D2 L3
#model= {'D4L3D4S2D4S2D2L3': 1}
#alpha = {'L3':{'asf':1,'abc':1}}
#digit = {'D4':{'5678': 2, '1234': 1},'D2':{'78':1}}
#specil = {'S2':{'#@':1,'..':1}}
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

# 将次数转化为频率
def probability(d):
    '''
    {'L3':{'asf':0.5,'abc':0.5}}
    {'D4': {'5678': 0.66,'1234': 0.33}, 'D2': {'78': 1}}
    '''
    for key in d.keys():
        num = sum(d[key].values())
        for k in d[key].keys():
            d[key][k] = d[key][k]*1.0 / num

# 将次数转化为频率
def base_probability(d):
    '''{'L3D4S3':0.25,'D4L3D4S2D4S2D2L3':0.75}'''
    num = sum(d.values())
    for key in d.keys():
        d[key] = d[key] * 1.0 / num

# 口令切割统计
def statistic(trainword):

    mode = {}
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
            s += m #L3D4S2D2
        if s in mode:
            mode[s] += 1
        else:
            mode.setdefault(s, 1)

    return mode, alpha, digit, special

# 由训练集中提取的字母段生成字典
def alphatodict(alpha):

    d = {}
    with open('wordlist.txt', 'w') as f:
        ''' a :{L3:{asf:1,egd:2},L2{io:3}}'''
        for key, value in alpha.items():
            for k in list(value.keys()):
                f.write(k+'\n') #asf\n


class Train:
    
    def __init__(self, bases, digits, symbols):
        
        self.bases = bases # 口令结构
        self.digits = digits # 数值字段
        self.symbols = symbols # 特殊符号字段
        self.alphas = {} # 字典  {L3:[asf,abc]}
        self.digitstats = {} # 训练集中每种类型数值字段出现的次数
        self.symbolstats = {} # 训练集中每种类型特殊符号字段出现的次数
        self.dictstats = {} # 字典中不同长度类型出现的次数
        self.dsize = 0 # 字典大小
    
    def order(self):
        
        probability(self.digits) # 计算数值字段出现的频率
        probability(self.symbols)  # 计算特殊符号字段出现的频率

        '''
        ***sorted返回的是列表***
        digits = {'D4': [('5678', 0.66), ('1234', 0.33)], 'D2': [('78', 1.0)]}
        digitstats = {'D4': 1, 'D2': 0}
        '''
        # 数值字段排序
        for key, value in self.digits.items():
            self.digits[key] = sorted(value.items(),key=lambda t:t[1], reverse=True)
            self.digitstats[key] = len(self.digits[key])-1
        # 特殊符号字段排序
        for key, value in self.symbols.items():
            self.symbols[key] = sorted(value.items(),key=lambda t:t[1], reverse=True)
            self.symbolstats[key] = len(self.symbols[key])-1
    # 导入字典
    def loadict(self, path):

        with open(path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                self.dsize += 1
                l = len(line)
                s = 'L' + str(l)
                if s not in self.alphas:
                    self.alphas[s] = []#{L3:[asf,abc]}
                self.alphas[s].append(line)
        for la in self.alphas:
            self.dictstats[la] = len(self.alphas[la])
            #{L3:2}