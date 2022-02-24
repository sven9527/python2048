#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#   @Filename :pygame2048.py
#   @Time     :2022/2/19 12:41 PM
#   @Author   :SvenZhang
"""
2048PYGAME版本
2048PYGAME版本
"""
import random
import sys
import pygame
import os

IS_DEBUG = False


class Config:
    """
     配置类
    """
    # 根目录
    rootdir = os.path.split(os.path.abspath(__file__))[0]
    # FPS
    FPS = 60
    # 屏幕大小
    SCREENSIZE = (650, 400)
    # 标题
    TITLE = '2048小游戏'
    # 背景颜色
    BG_COLOR = '#92877d'
    # 保存当前最高分的文件
    MAX_SCORE_FILEPATH = os.path.join(rootdir, 'score')
    # 一些必要的常量
    MARGIN_SIZE = 10
    BLOCK_SIZE = 100
    GAME_MATRIX_SIZE = (4, 4)
    # 背景音乐路径
    BGM_PATH = os.path.join(rootdir, 'music/nevada.mp3')
    # 字体路径
    FONT_PATH = os.path.join(rootdir, 'font/Hiragino Sans GB.ttc')


def log(*args):
    if IS_DEBUG:
        print(args)


class Py2048:

    def __init__(self):
        self.screen = None
        self.total_score = 0
        self.max_score = int(self.load_record())
        self.game_over = False
        self.over_reason = ''
        self.panel = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        self.init_main()
        self.resume()
        Py2048.load_and_play_music()

    def load_record(self):
        record = 0
        if os.path.exists(Config.MAX_SCORE_FILEPATH):
            with open(Config.MAX_SCORE_FILEPATH, 'r', encoding='utf-8') as f:
                record = f.read()
        return record

    def save_record(self):
        if self.total_score > self.max_score:
            with open(Config.MAX_SCORE_FILEPATH, 'w', encoding='utf-8') as f:
                f.write(str(self.total_score))

    @staticmethod
    def load_and_play_music():
        pygame.mixer.music.load(Config.BGM_PATH)
        pygame.mixer.music.play(-1, 0.0)

    def resume(self):
        """
        生成随机初始
        :return:
        """
        self.game_over = False
        self.total_score = 0
        for i in range(4):
            self.panel[i] = [random.choice([0, 0, 0, 2, 2, 4]) for j in range(4)]

    @staticmethod
    def add_same(vl, direction):
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
        res = Py2048.add_same(vl, direction)
        log('handle: ', vl, direction)
        score = 0
        while res[0]:
            score += res[1]
            res = Py2048.add_same(vl, direction)
            log('handle: ', vl, direction)
        return score

    def check_game_over(self):
        n = 0
        for q in self.panel:
            n += q.count(0)
        if n == 0:
            self.game_over = True
            self.over_reason = 'GAME OVER, YOU FAILED!'
        self.save_record()

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

    @staticmethod
    def get_color_by_number(number):
        '''
        根据方格当前的分数获得[方格背景颜色, 方格里的字体颜色
        '''
        number2color_dict = {
            0: ['#9e948a', '#776e65'],
            2: ['#eee4da', '#776e65'], 4: ['#ede0c8', '#776e65'], 8: ['#f2b179', '#f9f6f2'],
            16: ['#f59563', '#f9f6f2'], 32: ['#f67c5f', '#f9f6f2'], 64: ['#f65e3b', '#f9f6f2'],
            128: ['#edcf72', '#f9f6f2'], 256: ['#edcc61', '#f9f6f2'], 512: ['#edc850', '#f9f6f2'],
            1024: ['#edc53f', '#f9f6f2'], 2048: ['#edc22e', '#f9f6f2'], 4096: ['#eee4da', '#776e65'],
            8192: ['#edc22e', '#f9f6f2'], 16384: ['#f2b179', '#776e65'], 32768: ['#f59563', '#776e65'],
            65536: ['#f67c5f', '#f9f6f2'], 'null': ['#9e948a', '#776e65']
        }
        return number2color_dict[number]

    def draw_rect(self, pos, num):
        rect_ = (pos[0], pos[1], 100, 100)
        pygame.draw.rect(self.screen,
                         pygame.Color(Py2048.get_color_by_number(num)[0]),
                         rect=rect_)
        num_font = pygame.font.Font(Config.FONT_PATH, 40)
        font_color = pygame.Color(Py2048.get_color_by_number(num)[1])
        num_text = num_font.render(str(num), True, font_color)
        num_rect = num_text.get_rect()
        num_rect.center = (pos[0] + 50, pos[1] + 50)
        self.screen.blit(num_text, num_rect)

    def display_game_sf(self):
        self.screen.fill(Config.BG_COLOR)
        w, h = self.screen.get_size()
        for i in range(4):
            for j in range(4):
                pos = (j * 100, i * 100)
                self.draw_rect(pos, self.panel[i][j])
        self.draw_gameinfo()
        print('Total_Score: %s' % self.total_score)
        print('-*-' * 20)

    def init_main(self):
        pygame.init()
        # 设置窗口角标
        pygame.display.set_icon(
            pygame.image.load('images/icon.png')
        )
        self.screen = pygame.display.set_mode(Config.SCREENSIZE)
        self.screen.fill(pygame.Color(Config.BG_COLOR))
        pygame.display.set_caption(Config.TITLE)

    def draw_score(self):
        font_color = (255, 255, 255)
        font_size = 30
        font = pygame.font.Font(Config.FONT_PATH, font_size)
        text_max_score = font.render('Best: %s' % self.max_score, True, font_color)
        text_score = font.render('Score: %s' % self.total_score, True, font_color)
        start_x = Config.BLOCK_SIZE * Config.GAME_MATRIX_SIZE[1] + Config.MARGIN_SIZE
        self.screen.blit(text_max_score, (start_x + 10, 10))
        self.screen.blit(text_score, (start_x + 10, 20 + text_score.get_rect().height))
        start_y = 30 + text_score.get_rect().height + text_max_score.get_rect().height
        return (start_x, start_y)

    def draw_gameinfo(self):
        start_x, start_y = self.draw_score()
        start_y += 40
        font_color = (255, 255, 255)
        font_size_big = 20
        font_size_small = 10
        font_big = pygame.font.Font(Config.FONT_PATH, font_size_big)
        font_small = pygame.font.Font(Config.FONT_PATH, font_size_small)
        intros = ['TIPS:', 'Use arrow keys to move the number blocks.', 'Adjacent blocks with the same number will',
                  'be merged. Just try to merge the blocks as', 'many as you can!']
        for idx, intro in enumerate(intros):
            font = font_big if idx == 0 else font_small
            text = font.render(intro, True, font_color)
            self.screen.blit(text, (start_x + 10, start_y))
            start_y += text.get_rect().height + 10

    '''游戏结束界面'''

    def EndInterface(self):
        font_size_big = 45
        font_size_small = 22
        font_color = (255, 255, 255)
        font_big = pygame.font.Font(Config.FONT_PATH, font_size_big)
        font_small = pygame.font.Font(Config.FONT_PATH, font_size_small)
        surface = self.screen.convert_alpha()
        surface.fill((127, 255, 212, 2))
        text = font_big.render(self.over_reason, True, font_color)
        text_rect = text.get_rect()
        text_rect.centerx, text_rect.centery = Config.SCREENSIZE[0] / 2, Config.SCREENSIZE[1] / 2 - 50
        surface.blit(text, text_rect)
        button_width, button_height = 100, 40
        button_start_x_left = Config.SCREENSIZE[0] / 2 - button_width - 20
        button_start_x_right = Config.SCREENSIZE[0] / 2 + 20
        button_start_y = Config.SCREENSIZE[1] / 2 - button_height / 2 + 20
        pygame.draw.rect(surface, (0, 255, 255), (button_start_x_left, button_start_y, button_width, button_height))
        text_restart = font_small.render('Restart', True, font_color)
        text_restart_rect = text_restart.get_rect()
        text_restart_rect.centerx, text_restart_rect.centery = button_start_x_left + button_width / 2, button_start_y + button_height / 2
        surface.blit(text_restart, text_restart_rect)
        pygame.draw.rect(surface, (0, 255, 255), (button_start_x_right, button_start_y, button_width, button_height))
        text_quit = font_small.render('Quit', True, font_color)
        text_quit_rect = text_quit.get_rect()
        text_quit_rect.centerx, text_quit_rect.centery = button_start_x_right + button_width / 2, button_start_y + button_height / 2
        surface.blit(text_quit, text_quit_rect)
        while True:
            self.screen.blit(surface, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Py2048.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button:
                    if text_quit_rect.collidepoint(pygame.mouse.get_pos()):
                        return False
                    if text_restart_rect.collidepoint(pygame.mouse.get_pos()):
                        return True
            pygame.display.update()

    @staticmethod
    def quit_game():
        pygame.quit()
        sys.exit()

    def run(self):
        clock = pygame.time.Clock()
        self.display_game_sf()
        while True:
            op = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Py2048.quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        op = 'a'
                    elif event.key == pygame.K_RIGHT:
                        op = 'd'
                    elif event.key == pygame.K_UP:
                        op = 'w'
                    elif event.key == pygame.K_DOWN:
                        op = 's'
            if op:
                # 对数字矩阵进行操作
                self.operation(op)
                # 检查游戏是否结束
                self.check_game_over()
                if self.game_over:
                    self.game_over = True
                # 在随机位置补充数字
                self.put_random_num()
                self.display_game_sf()

            pygame.display.update()
            clock.tick(Config.FPS)

            if self.game_over:
                if not self.EndInterface():
                    Py2048.quit_game()
                else:
                    self.__init__()
                    self.display_game_sf()


if __name__ == '__main__':
    game = Py2048()
    game.run()
