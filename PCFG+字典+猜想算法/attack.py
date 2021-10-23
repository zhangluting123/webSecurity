import argparse
from collections import OrderedDict

from prac.guess_mine import *
from prac.train_mine import *

import os


def main():

    if(not os.path.exists('guess')):
        os.mkdir('guess')

    trainword = loadpass('trainword.txt')    # 导入训练集
    oribase, orialpha, oridigit, orispecial = statistic(trainword)

    alphatodict(orialpha)   # 字典由训练集中提取的英文字母字段生成，生成wordlist.txt

    base_probability(oribase)   # 每种口令结构出现的频率
    '''
    # oribase={'L3D4S3':0.25,'D2L3D5S1':0.75}
    # oribase.items()=[('L3D4S3':0.25),('D2L3D5S1':0.75)]
    '''
    oribase = sorted(oribase.items(), key=lambda t: t[1], reverse=True)    # 排序[根据频率降序]
    testword = load_testword('testword.txt')    # 导入测试集
    true_guess = 0    # 统计猜解次数
    num_guess = 0    # 统计猜解正确的次数

    for i in oribase:    # 每次使用一种类型的口令结构去猜解
        base = OrderedDict([i])
        alpha = copy.deepcopy(orialpha)
        digit = copy.deepcopy(oridigit)
        special = copy.deepcopy(orispecial)

        model = Train(base, digit, special)
        model.order()
        model.loadict('wordlist.txt')  #这句话以后才有的model.alpha
        ''' alpha={'L3':{'asf':0.5,'abc':0.5}} 频率'''
        probability(alpha)

        # 开始猜测口令
        guesser = Guess(model, testword, alpha)
        guesser.initqueue()   # 初始化队列
        while True:
            preterminal = guesser.queueinsert()#根据训练集优先队列作出所有编码可能情况
            if guesser.flag:    # 判断队列是否为空
                print(preterminal[1])#控制台显示各种密码结构
                guesser.guesspw(preterminal)  #生成猜解口令，将密码结构中Lm替换成字典
            else:
                break
        true_guess += guesser.true_guess
        num_guess += guesser.num_guess
        testword = guesser.testword
        with open('memory.txt', 'a+') as memory:
            memory.write(str(true_guess) + ' / ' + str(num_guess) + '\n')

if __name__ == "__main__":
    main()


