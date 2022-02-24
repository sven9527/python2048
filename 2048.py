#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#   @Filename :2048.py
#   @Time     :2022/2/18 8:22 PM
#   @Author   :SvenZhang
"""
2048字符版本
2048字符版本
2048字符版本
"""
import random
import sys

IS_DEBUG = False
# 操作方向
OPERATION = ['w', 'a', 's', 'd', 'q']


def log(*args):
    if IS_DEBUG:
        print(args)


class Game2048:

    def __init__(self):
        self.total_score = 0
        self.game_over = False
        self.over_reason = ''
        self.panel = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

    def resume(self):
        """
        生成随机初始
        :return:
        """
        self.game_over = False
        self.total_score = 0
        for i in range(4):
            self.panel[i] = [random.choice([0, 0, 0, 2, 2, 4]) for j in range(4)]

    def display(self):
        blank_str = ' ' * 2
        for i in range(4):
            for j in range(4):
                print('{:>4d}'.format(self.panel[i][j]), end=blank_str)
                if j == 3 and i != 3:
                    print('\n')
        print('Total_Score: %s' % self.total_score)
        print('=*=' * 20)

    def run(self):
        self.resume()
        while True:
            self.display()
            op = input('Input: W(Up) S(Down) A(Left) D(Right) Q(quit!), press <CR>.\n')
            if op.lower() not in OPERATION:
                continue
            if op.lower() == 'q':
                print('Bye')
                sys.exit(0)
            # 对数字矩阵进行操作
            self.operation(op)
            # 检查游戏是否结束
            self.check_game_over()

            if self.game_over:
                print(self.over_reason)
                print('Your total score: ', self.total_score)
                sys.exit(0)
            # 在随机位置补充数字
            self.put_random_num()

    def add_same(self, vl, direction):
        """
        相邻的相同数字相加
        :return:
        """
        score = 0
        log('add_same: ', vl, direction)
        if direction in ['a', 'w']:
            for i in [0, 1, 2]:
                if vl[i] == vl[i + 1] != 0:
                    vl[i] *= 2
                    vl[i + 1] = 0
                    score += vl[i]
                    return [True, score]
        elif direction in ['d', 's']:
            for i in [3, 2, 1]:
                if vl[i] == vl[i - 1] != 0:
                    vl[i] *= 2
                    vl[i - 1] = 0
                    score += vl[i]
                    return [True, score]
        return [False, score]

    def align(self, vl, direction):
        """
        对齐非0数字
        direction=left [8,0,0,2] ===> [8,2,0,0]
        """
        for i in range(vl.count(0)):
            vl.remove(0)
        zeros = [0 for x in range(4 - len(vl))]
        if direction in ['a', 'w']:
            vl.extend(zeros)
        elif direction in ['d', 's']:
            vl[:0] = zeros
        return vl

    def handle(self, vl, direction):
        """
        处理一行或一列滑动后的计算
        """
        self.align(vl, direction)
        res = self.add_same(vl, direction)
        log('handle: ', vl, direction)
        score = 0
        while res[0]:
            score += res[1]
            res = self.add_same(vl, direction)
            log('handle: ', vl, direction)
        return score

    def check_game_over(self):
        n = 0
        for q in self.panel:
            n += q.count(0)
        if n == 0:
            self.game_over = True
            self.over_reason = 'GAME OVER, YOU FAILED!'
        if self.total_score >= 2048:
            self.game_over = True
            self.over_reason = 'GAME OVER, YOU WIN!!!'

    def put_random_num(self):
        """
        在随机空白处添加随机生成的数字
        2和4按3：1比例出现
        :return:
        """
        if self.game_over:
            return
        num = random.choice([2, 2, 2, 4])
        pos = random.randrange(1, num + 1)
        n = 0
        for i in range(4):
            for j in range(4):
                if self.panel[i][j] == 0:
                    n += 1
                    if n == pos:
                        self.panel[i][j] = num
                        break

    def operation(self, op):
        """
        根据op操作重新计算矩阵值
        :param op:
        :return:
        """
        op = op.lower()
        if op in ['a', 'd']:
            # 左移、右移 每次拿一行处理
            for i in range(len(self.panel)):
                score = self.handle(self.panel[i], op)
                self.total_score += score
        elif op in ['w', 's']:
            # 上移、下移 每次拿一列处理
            for i in range(len(self.panel[0])):
                row = [self.panel[0][i], self.panel[1][i], self.panel[2][i], self.panel[3][i]]
                score = self.handle(row, op)
                self.panel[0][i], self.panel[1][i], self.panel[2][i], self.panel[3][i] = row[0], row[1], row[2], row[3]
                self.total_score += score


if __name__ == '__main__':
    g = Game2048()
    g.run()
