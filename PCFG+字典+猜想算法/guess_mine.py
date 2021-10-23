import re
import sys
import copy
from queue import PriorityQueue
import itertools

Lp = re.compile('L')#字母
Dp = re.compile('D')
Sp = re.compile('S')

# 导入测试集
def load_testword(path):
    
    testword = {}
    with open(path, encoding='utf-8', errors='ignore') as wordList:
        for line in wordList:
            word = line.strip()
            if word in testword:
                testword[word] += 1
            else:
                testword.setdefault(word, 1)
    return testword

def parsebase(base):
    # 'L6D1' --> ['L6','D1']
    pa = re.compile(r'[LDS]\d+', re.ASCII)
    baseList = re.findall(pa, base)
    return baseList
'''
alphas=[[4, '3'],[21, '2']]
'''
def findalphas(base):
    
    alphas = []
    for i, s in enumerate(base):
        if Lp.match(s):
            index = extractindex(base, i)
            alphas.append(index)
    return alphas
'''
base = ['D4','L3','D4','S2','D4','S2','D2','L3']
i=        0,   1,   2,   3,   4,   5,   6,   7
index[0]= 0,   4,   7   11   13   17   19   21
index[1]='4'  '3'  '4'  '2'  '4'  '2'  '2'  '3'
'''
def extractindex(base, pv):
    # index[0]: pv点之前字段总长度
    # index[1]: 当前pv点字段长度
    index = [0] * 2
    prev = "".join(base[0: pv])                #L3D4S2返回数字格式列表[3,4,2]
    index[0] = sum(map(int, re.findall(r'\d+', prev)))
    index[1] = re.search(r'\d+', base[pv]).group()#group()分组截获字符串

    return index

class Guess:
    
    def __init__(self, model, testword, pwalpha):
        
        self.model = model
        self.num_guess = 0     # 总共猜测的次数
        self.true_guess = 0    # 猜测正确的次数[包括重复密码]
        self.queue = PriorityQueue()
        self.testword = testword
        self.pwalpha = pwalpha #{'L3':{'asf':0.5,'abc':0.5}}
        self.flag = 1

    # 初始化队列
    def initqueue(self):
        # d = {'D4L3D4S2D4S2D2L2': 0.75,'L3D4S3': 0.25}
        for base in self.model.bases:
            '''
            0  1  2  3  4  5
              [ ] 0        [ ]
              qobject[1]=['D4','L3','D4','S2','D4','S2','D2','L3']
              qobject[5]=['D4','L3','D4','S2','D4','S2','D2','L3']
              prob=0.75
            '''
            qobject = [None] * 6
            qobject[1] = parsebase(base)    # 'L6D1' --> ['L6','D1']
            qobject[5] = parsebase(base)    # 'L6D1' --> ['L6','D1']
            qobject[2] = 0    #
            prob = self.model.bases[base]  #频率
            
            preterminal = ""
            
            for i, s in enumerate(qobject[1]):
                '''
                i=   0    1    2    3    4    5    6    7
                s= 'D4','L3','D4','S2','D4','S2','D2','L3'
                alphaindex = [[4,'3'],[21,'3']]
                digitstats = {'D4':1,'D2':0}
                symbolstats = {'S2':1}
                model.alpha = {'L3':['asf','abc']}
                digits = {'D4':[('5678',0.66), ('1234',0.33)], 'D2':[('78',1.0)]}
                symbols = {'S2':[('#@',0.5),('..',0.5)]}
                preterminal = 5678-L3-5678-#@-5678-#@-78-L3
                qobject[5][i] = 5678/---/5678/#@/5678/#@/78/---
                
                prob = 0.75*0.6 * 0.6 * 0.5 * 0.6 * 0.5 * 1
                '''
                if Lp.match(s):
                    preterminal += s
                    continue
                else:
                    if Dp.match(s): #
                        preterminal += self.model.digits[s][0][0]
                        qobject[5][i] = self.model.digits[s][0][0]
                        prob *= self.model.digits[s][0][1]    # 口令概率值
                    elif Sp.match(s):
                        preterminal += self.model.symbols[s][0][0]
                        qobject[5][i] = self.model.symbols[s][0][0]
                        prob *= self.model.symbols[s][0][1]    # 口令概率值
                    else:
                        print("error")
                        sys.exit(1)
            if prob < 0.000001:    # 如果该口令模式的概率值小于0.000001,则不进入队列
                continue
            '''
            preterminal = 5678L35678#@5678#@78L3
            qobject[0] = 0.75*0.6 * 0.6 * 0.5 * 0.6 * 0.5 * 1 = xxx
            qobject[1]=['D4','L3','D4','S2','D4','S2','D2','L3']
            qobject[2] = 0 
            qobject[3] = 5678L35678#@5678#@78L3
            qobject[4] = [0, 0, 0, 0, 0, 0, 0, 0]
            qobject[5] = {5678,L3,5678,#@,5678,#@,78,L3}
            '''
            qobject[3] = preterminal
            qobject[4] = [0] * len(qobject[1])
            qobject[0] = prob
            self.queue.put(qobject)

    # 插入队列
    def queueinsert(self):
        
        if self.queue.empty():    # 判断队列是否为空
            print("all possible gussess have be output")
            print("GUESS:", self.true_guess)
            print("TRUE:", self.num_guess)
            self.flag = 0
            return
           
        qobject = self.queue.get()
        pv = qobject[2]    # 指示下一个替换的位置
        base = qobject[1]
        alphaindex = findalphas(base)#alphaindex=[[4, '3'],[21, '2']]
        
        for i, s in enumerate(base):
            if i < pv or Lp.match(s): #跳过字母位置
                continue
            index = extractindex(base, i)
            if Dp.match(s) and qobject[4][i] == self.model.digitstats[s]:     # 判断同类型字段是否遍历完[0==1(还有一个)]
                continue
            if Sp.match(s) and qobject[4][i] == self.model.symbolstats[s]:     # 判断同类型字段是否遍历完
                continue
            newobject = copy.deepcopy(qobject)
            newobject[2] = i     # 设置pv值
            newobject[4][i] += 1   # 指示该字段列表中下一个替换的位置
            if Dp.match(s):
                original = self.model.digits[s][qobject[4][i]] #D4的0号、  1
                new = self.model.digits[s][newobject[4][i]] #D4的1号
                newobject[5][i] = new[0]  #qobject[5] = {1234,L3,5678,#@,5678,#@,78,L3}
            else:
                original = self.model.symbols[s][qobject[4][i]]
                new = self.model.symbols[s][newobject[4][i]]
                newobject[5][i] = new[0]
            newobject[0] = qobject[0] / original[1] * new[1] #新概率= 原概率/0.66*0.33
            newobject[3] = ''.join(newobject[5])             #1234L35678#@5678#@78L3
            if newobject[0] < 0.000001:    # 如果该口令模式的概率值小于0.000001,则不进入队列
                continue
            self.queue.put(newobject)
            
        return (alphaindex, qobject[3], qobject[0])

    # 生成猜解口令
    def guesspw(self, preterminal):
        # 字母位置[[4, '3'],[21, '3]]，起始结构，起始概率
        alphaindex = preterminal[0] #[[4, '3'],[21, '3']]
        pw = preterminal[1]
        pro = preterminal[2]
        num = 0
        if not alphaindex:
            # print(pw)
            pass
        else:
            replacements = []
            for index in alphaindex:    # 一个口令结构模式中可能含有多个'L'字段
                s = 'L' + index[1]
                replacements.append(self.model.alphas[s]) #model.alphas = {'L3':['asf','abc']}
            # [['a', 'b'], ['ab', 'cd']] --> [('a','ab'),('a', 'cd'),('b','ab'),('b','cd')]
            # replacements =[['asf', 'abc']['asf', 'abc']]
            replacements = list(itertools.product(*replacements)) #replacements = [('asf', 'asf'), ('asf', 'abc'), ('abc', 'asf'), ('abc', 'abc')]
            filepath = './guess/' + list(self.model.bases.keys())[0] + '.txt'
            with open(filepath, mode='a+') as f:
                for rep in replacements:
                    pwd = pw
                    pwdpro = pro
                    # 将字母所在位置替换为字符串,替换次数≤1
                    for i, word in enumerate(rep):
                        start = alphaindex[i][0]        #4    21
                        s = 'L' + alphaindex[i][1]      #L3   L3
                        pwd = pwd.replace(s, word, 1)
                        pwdpro *= self.pwalpha[s][word] #{'L3':{'asf':0.5,'abc':0.5}} 结构概率*L3的asf概率
                    if pwdpro < 0.000000001:    # 如果该口令的概率值小于0.000000001,则不进行猜解
                        # print('..................................................' + str(self.num_guess))
                        continue
                    num += 1
                    f.write(pwd + '\t' + str(pwdpro) + '\n')
                    if pwd in self.testword:
                        self.true_guess += self.testword[pwd]
                        del self.testword[pwd]
        self.num_guess += num
