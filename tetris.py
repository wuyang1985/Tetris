#coding=utf-8
#qpy:2
#qpy:kivy
#from __future__ import division
import logging

import time, sys, os, re, string

print ("os.path.abspath：", os.path.abspath("./"))
os.environ['KIVY_HOME'] = os.path.join(os.path.abspath("./"), ".kivy")

from threading  import Lock
from kivy.app import App
from kivy.uix.widget import Widget
#from kivy.lang import Builder
from kivy.config import Config, ConfigParser
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty,BooleanProperty, ConfigParserProperty, StringProperty
from kivy.vector import Vector
from random import randint
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import  BoxLayout

from kivy.uix.button import Button
from kivy.uix.image import  Image
from kivy.uix.behaviors import ButtonBehavior

from kivy.clock import Clock

SOUND_BACKGROUND  = 100
SOUND_MOVE_TO_END = 0
SOUND_MOVE        = 1
SOUND_MOVE_FAIL   = 2
SOUND_CHANGE      = 3
SOUND_CHANGE_FAIL = 4
SOUND_CANCEL      = 5
SOUND_MOVE_FASTER = 6
#SOUND_UPGRADE     = 6


from kivy.core.audio import SoundLoader
gSoundBackground    = SoundLoader.load('background.mp3')
gSoundMoveToEnd     = SoundLoader.load('DownToEnd.WAV')
gSoundMove          = SoundLoader.load('Move.WAV') 
gSoundMoveFail      = SoundLoader.load('MoveFailed.WAV')
gSoundChange        = SoundLoader.load('Change.WAV')
gSoundChangeFail    = SoundLoader.load('ChangeFail.WAV')
gSoundCancel        = SoundLoader.load('Cancel.WAV')
gSoundMoveFaster    = SoundLoader.load('MoveFaster.WAV')
#gSoundMoveFaster    = SoundLoader.load('MoveDownFaster.WAV')


def SoundPlay(soundType):
    if soundType == SOUND_MOVE_TO_END:
        gSoundMoveToEnd.play()
    elif soundType == SOUND_MOVE:
        gSoundMove.play()
    elif soundType == SOUND_MOVE_FAIL:
        gSoundMoveFail.play()
    elif soundType == SOUND_CHANGE:
        gSoundChange.play()
    elif soundType == SOUND_CHANGE_FAIL:
        gSoundChangeFail.play()
    elif soundType == SOUND_CANCEL:
        gSoundCancel.play()
    elif soundType == SOUND_MOVE_FASTER:
        gSoundMoveFaster.play()
    elif soundType == SOUND_BACKGROUND:
        gSoundBackground.play()
    # elif soundType == SOUND_MOVE:
        # gSoundMove.play()
    # elif soundType == SOUND_MOVE:
        # gSoundMove.play()

def SoundRePlay(obj):
    SoundPlay(SOUND_BACKGROUND)
    
gSoundBackground.bind(on_stop=SoundRePlay)  
   
SoundPlay(SOUND_BACKGROUND)       

MOVE_NONE      = -1
MOVE_DOWN      = 0
MOVE_LEFT      = 1
MOVE_RIGHT     = 2
MOVE_CHANGE    = 3
move_name = ["DOWN", "LEFT", "RIGHT", "CHANGE"]

#每个俄罗斯方块由外框 与 内实框组成
outline_width = 50
border_len = 4
outline_rect_len = (outline_width-border_len*2)
rect_border_len = 8
inner_rect_len   = (outline_rect_len-rect_border_len*2)

OUT_BORDER_SIZE=(outline_width, outline_width)
INNER_SOLID_SIZE=(outline_rect_len, outline_rect_len)

UNIT_BORDER_SIZE=(50,50)  #俄罗斯方块外框的大小
UNIT_SIZE = (45,45)       #俄罗斯方块内填充Rect的大小
MAX_COLS_NUM = 12           #俄罗斯方块最大列数
MAX_ROWS_NUM = 24           #俄罗斯方块最大行数
BK_SIZE = (50,50)
COLOR_DIC = {'RED':[1,0,0], 'BLUE':[0,0,1], 'WHITE':[1,1,1], 'BLACK':(0,0,0), 'BACKGROUND':[0.7, 0.7, 0.7],\
             'GRAY':[0.7, 0.7, 0.7]}


BORDER_LEFT     = 0
BORDER_RIGHT    = 1
BORDER_BOTTOM   = 2
BORDER_TOP      = 3

#logger模块设置
# logger = logging.getLogger('LOG')
# logger.setLevel(logging.NOTSET)
# formatter = logging.Formatter('[%(pathname)s]%(asctime)s[%(name)s][%(levelname)s]::%(message)s')# 创建输出格式
# consoleHandler = logging.StreamHandler()    # 配置控制台Handler并设置等级为DEBUG
# consoleHandler.setLevel(logging.DEBUG)
# consoleHandler.setFormatter(formatter)      # 为handler添加fromatter
# logger.addHandler(consoleHandler)           # 将Handler加入logger

kivy_cfg = Config.get_configparser("kivy")
print kivy_cfg.filename

# config = ConfigParser("app")
app_cfg = Config.get_configparser("app")
#print app_cfg.filename

def GetScores(cancel_lines, level):
    if cancel_lines == 1:
        return 100*level
    elif cancel_lines == 2:
        return 150*level
    elif cancel_lines == 3:
        return 300*level
    elif cancel_lines == 4:
        return 800*level


def setColor(dict):
    Color(dict[0], dict[1], dict[2])


class CustomLine(Widget):
    line_width = NumericProperty(1.0)
    line_clr   = ListProperty([])

    def __init__(self, **kwargs):
        super(CustomLine, self).__init__(**kwargs)
        self.line_width = 5
        self.line_clr = [0, 0, 0]

class CustomRect(Widget):
    rect_clr = ListProperty([])
    def __init__(self, **kwargs):
        super(CustomRect, self).__init__(**kwargs)
        self.rect_clr = [0, 0, 0]

class ControlPanelWidget(Widget):
    pass

class Tetris(Widget):
    #活动方块相对运行区域（左下角）的相对位置，
    #如10行10列的活动区域，方块中心点起始位置应该在10行5列，对应行列索引是(9, 4)
    init_base_x = NumericProperty(0)
    init_base_y = NumericProperty(0)
    init_base = ReferenceListProperty(init_base_x, init_base_y)

    #活动方块的中心点在活动区域的base会随着移动不断变化
    base_x = NumericProperty(0)
    base_y = NumericProperty(0)
    base = ReferenceListProperty(base_x, base_y)

    #方块单元的大小
    size_width = NumericProperty(0)
    size_height = NumericProperty(0)
    tetris_size = ReferenceListProperty(size_width, size_height)

    # 当前活动区域的列数与行数
    cols = NumericProperty(0)
    rows = NumericProperty(0)  # 最大行
    activity_size = ReferenceListProperty(cols, rows)

    #九宫格以base为中心 每一个节点的轨迹图   -1 -1下一步就是0 -1； -1 0下一步就是-1 -1
    #九宫格变形，需要判断下一个形状的节点的位置是否为空，还需要判断当前每个节点的下一步位置是否为0  若下一步已经在当前形状里，要删除
    #九宫格默认为逆时针方向
    
    tetris_tuple = (
                     (((0,0),),), #九宫格中心
                     (((0,0),(0,-1)),((0,0),(1,0))),
                     (((0,0),(-1, 0),(0,-1)),((0,0),(-1,0),(0,1)),((0,0),(1, 0),(0,1)),((0,0),(0, -1),(1,0))),
                     (((0,0),(1,0),(1,-1),(-1,0)),((0,0),(0,-1),(-1,-1),(0, 1)),((0,0),(1,0),(-1,0),(-1,1)),((0,0),(0,-1),(0,1),(1,1))),
                     (((0,0),(1,1),(1,0),(-1,0)),((0,0),(1,-1),(0,-1),(0, 1)), ((0,0),(1,0),(-1,-1),(-1,0)),((0,0),(0,-1),(-1,1),(0,1))),
                     (((0,0),(1,0),(-1,0),(0,1)),((0,0),(0,-1),(0,1),(1,0)),((0,0),(-1,0),(1,0),(0,-1)), ((0,0),(-1,0),(0,-1),(0,1))),
                     (((0,0),(-1,-1),(-1,0),(0,1)),((0,0),(-1,1),(0,1),(1,0))),
                     (((0,0),(0,-1),(-1,0),(-1,1)),((0,0),(-1,0),(0,1),(1,1))),
                     (((0,0),(0,-1),(-1,0),(-1,-1),),),
                     (((0,0),(0,1),(0,-1),(0,-2)),((0,0),(-1,0),(-2,0),(1,0)))
                   )
    
    #对应tetris_tuple中 变形到下一个形状所经过的点（基于中心点）
    #如 ((0,0),(0,-1))变成到((0,0),(1,0))，需要经过（1, -1)这个点，在变形前需要判断barrier位置处是否已有方块
    tetris_barrier = (
                        ((()),),
                        (((-1,-1),),),
                        (((-1,-1),(-1, 1)),((-1,1),(1, 1)),((1,1),(1,-1)),((1,-1),(-1,-1))),
                        (((-1,1),),((1,1),),((1,-1),),((-1,-1),)),
                        (((-1,1),),((1,1),),((1,-1),),((-1,-1),)),
                        (((-1,1),(1,1),(1,-1)),((-1,-1),(1,1),(1,-1)),((1,-1),(-1,-1),(-1,1)),((-1,-1),(-1,1),(1,1))),
                        (((1,  1),),),
                        (((-1,-1),),),
                        ((()),),
                        (((-1, 1),(1,-2),(1,-1),(2,-1),(2,-2)),)
                     )
                     
    def __init__(self, **kwargs):
        super(Tetris, self).__init__(**kwargs)
        
        #方块在tetris_tuple中的索引
        self.block_idx = 0
        self.shape_idx = 0
        
        self.tetris = 0  #没有创建具体方块
        
        #每个方块相对其中心点 上 下 左 右的间隔  静态保存在tetris_barrier
        self.border = [0, 0, 0, 0]
        self.next_tetris = None

        self.FallTimer     = None
        self.fall_interval  = 3.0
        self.quicken   = False
        
        #当前方块的活动区域
        self.actTetrisPanel = None
        
        self.actMoveType = MOVE_NONE
        
        self.downToEnd = False
        
        #下一个活动方块
        self.nextTetrisObj = None
        
        #是否已经移动一次：移动按钮按下并立即释放，cancel可能会在timer运行前就取消，类似这种场景在cancel里移动一次
        self.once_move_done = False
        self.pause = False
        self.stop = 0
        
        self.actMoveTimer = None
        self.actChangeTimer = None
        
        self.mutex = Lock()
    
    def StartTimer(self):     
        self.fall_interval = 2.0
        self.FallTimer = Clock.schedule_interval(self.Fall, 1.0 / self.fall_interval)
        
        self.move_interval = self.fall_interval*5
        self.MoveTimer = Clock.schedule_interval(self.Move, 1.0 / self.move_interval)
    
    #移动之前检测方块下一个位置所有点对应的viewTable是否有方块(==1)，有就不能移动
    def IsMoveAllowed(self, dir):    
        base_x         = self.base_x
        base_y         = self.base_y
        tetrisTuple    = self.tetris
        tetrisLen      = len(tetrisTuple)
        view_table     = self.actTetrisPanel.view_table
        
        if dir == MOVE_DOWN:
          for i in range(0, tetrisLen):    #非中心点下一个位置是否有方块                  
                if view_table[tetrisTuple[i][1]+base_y-1][tetrisTuple[i][0]+base_x]==1:
                    return False
                    
        elif dir == MOVE_LEFT:         
            for i in range(0, len(tetrisTuple)):
                if view_table[tetrisTuple[i][1]+base_y][tetrisTuple[i][0]+base_x-1]==1:
                    return False
                    
        elif dir == MOVE_RIGHT:         
            for i in range(0, len(tetrisTuple)):
                if view_table[tetrisTuple[i][1]+base_y][tetrisTuple[i][0]+base_x+1]==1:
                    return False
                    
        return True
    
    #加速下落
    def move_down_faster(self):
        rapid_fall_interval = 50.0    
        if self.quicken == True:
            self.quicken = False
            self.FallTimer.cancel()
            self.FallTimer = Clock.schedule_interval(self.Fall, 1.0 / (self.fall_interval))
        else:
            self.quicken = True
            self.FallTimer.cancel()
            self.FallTimer = Clock.schedule_interval(self.Fall, 1.0 / rapid_fall_interval)
            SoundPlay(SOUND_MOVE_FASTER)            
        
    #升级
    def UpgradeLevel(self):
        self.fall_interval += 1.0
        logging.debug("fall_interval upgrade to [%d]", self.fall_interval)
        self.FallTimer.cancel()
        self.FallTimer = Clock.schedule_interval(self.Fall, 1.0 / self.fall_interval)
        
        self.MoveTimer.cancel()
        self.move_interval = self.fall_interval*2
        self.MoveTimer = Clock.schedule_interval(self.Move, 1.0 / self.move_interval)
    
    def Fall(self, dt):
        if self.stop ==1:
            self.actTetrisPanel.GameOver()
            return
            
        if self.downToEnd==True: 
            SoundPlay(SOUND_MOVE_TO_END)
            self.downToEnd = False
            logging.debug("downToEnd is False")
            
            if False == self.CreateTetris(self.nextTetrisObj.block_idx, self.nextTetrisObj.shape_idx):
                self.stop = 1
                self.actTetrisPanel.GameOver()
                return
            
            self.nextTetrisObj.CreateRandomTetris(True)
            self.quicken = False
            self.FallTimer.cancel()
            self.FallTimer = Clock.schedule_interval(self.Fall, 1.0 / self.fall_interval)
            #if self.border[BORDER_TOP] > 0:
            #    self.base_y  -= self.border[BORDER_TOP]
            #print "new tetrisList x, y ", self.tetrisList, self.base_x, self.base_y
            #TODO  新生的方块有可能到顶了
            
        else:
            self.mutex.acquire()
            if self.base_y + self.border[BORDER_BOTTOM] == 0 or False == self.IsMoveAllowed(MOVE_DOWN):
                self.downToEnd = True
                logging.debug("downToEnd is True")
                self.canvas.clear()
                self.actTetrisPanel.RefreshTetrisView()
                
            else:             
                self.start_move(MOVE_DOWN)
            self.mutex.release()
           
    def Pause(self):
        if self.pause == True:
            self.pause = False
            self.FallTimer = Clock.schedule_interval(self.Fall, 1.0 / self.fall_interval)
        else:
            self.pause = True
            self.FallTimer.cancel()
    
    def Change(self):
        self.mutex.acquire()
        if True == self.change_allowed():
            SoundPlay(SOUND_CHANGE)
            block_idx = self.block_idx
            shape_idx = self.shape_idx  # 由于每获取一个当前的方块时，都会自动获取下一个方块的tuple，这里shape_idx不能更新
            if shape_idx == len(self.tetris_tuple[self.block_idx]) - 1:
                shape_idx = 0
            else:
                shape_idx += 1

            self.get_tetris(self.block_idx, shape_idx)
            self.get_next_tetris()
            self.get_barrier()
            self.border         = self.get_border(self.block_idx, self.shape_idx)
            self.next_border    = self.get_border(self.block_idx, self.shape_idx + 1)
            print "tetris change:", self.tetris, "border:", self.border, "next_tetris:", self.next_tetris, "next border:", self.next_border
            self.draw()
        else:  
            SoundPlay(SOUND_CHANGE_FAIL)
        self.mutex.release()
        
    def ChangeCancel(self):
        if self.actChangeTimer == None:
            print "ChangeCancel::actChangeTimer is None"
            return
        self.actChangeTimer.cancel()
    
    def Move(self, dt):
        #若已到达最后就不要再去移动
        if self.downToEnd == True:
            return 
            
        self.mutex.acquire()
        if self.actMoveType == MOVE_LEFT:
            if self.base_x+self.border[BORDER_LEFT] == 0:
                self.mutex.release()
                return
            elif True == self.IsMoveAllowed(MOVE_LEFT):
                self.start_move(MOVE_LEFT)
                self.once_move_done = True
        elif self.actMoveType == MOVE_RIGHT:
            if self.base_x+self.border[BORDER_RIGHT] == self.cols-1:
                self.mutex.release()
                return
            elif True == self.IsMoveAllowed(MOVE_RIGHT):
                self.start_move(MOVE_RIGHT)
                self.once_move_done = True
        
        self.mutex.release() 
        
    def MoveStartTimer(self, dt):
        #若已到达最后就不要再去移动
        if self.downToEnd == True:
            return 
            
        self.mutex.acquire()
        if self.actMoveType == MOVE_LEFT:
            if self.base_x+self.border[BORDER_LEFT] == 0:
                self.mutex.release()
                return
            elif True == self.IsMoveAllowed(MOVE_LEFT):
                self.start_move(MOVE_LEFT)
                self.once_move_done = True
        elif self.actMoveType == MOVE_RIGHT:
            if self.base_x+self.border[BORDER_RIGHT] == self.cols-1:
                self.mutex.release()
                return
            elif True == self.IsMoveAllowed(MOVE_RIGHT):
                self.start_move(MOVE_RIGHT)
                self.once_move_done = True
        
        self.mutex.release() 
    
    def MoveLeft(self):
        print ("MoveLeft")
        if self.actMoveType == MOVE_RIGHT or self.actMoveType == MOVE_LEFT:
            return
        self.actMoveType = MOVE_LEFT
        #左右移timer只创建一次，多次创建会导致移动速度越来越快，类似多个timer叠加运行
        #self.actMoveTimer = Clock.schedule_interval(self.MoveStartTimer, 1.0 / self.timer_interval)
              
    def MoveRight(self):
        print ("MoveRight")
        if self.actMoveType == MOVE_RIGHT or self.actMoveType == MOVE_LEFT:
            return
        self.actMoveType = MOVE_RIGHT
        #self.actMoveTimer = Clock.schedule_interval(self.MoveStartTimer, 1.0 / self.timer_interval)
          
    def MoveCancel(self):
        self.actMoveType = MOVE_NONE
        
        #快速按移动按键时，方块还没有到底之前按下移动按键就确保移动一次。
        # if self.downToEnd != True and self.once_move_done != True:
        #     self.mutex.acquire()
        #     if self.actMoveType == MOVE_LEFT:
        #         if self.base_x+self.border[BORDER_LEFT] > 0 \
        #         and True == self.IsMoveAllowed(MOVE_LEFT):
        #             self.start_move(MOVE_LEFT)
        #     elif self.actMoveType == MOVE_RIGHT:
        #         if self.base_x+self.border[BORDER_RIGHT] < self.cols-1 \
        #         and True == self.IsMoveAllowed(MOVE_RIGHT):
        #             self.start_move(MOVE_RIGHT)
        #     self.mutex.release()
        #
        # self.once_move_done = False
        # if self.actMoveTimer != None:
        #     self.actMoveTimer.cancel()
        # self.actMoveType = MOVE_NONE
        
    def check_collision(self, tetris_tuple, dir=-1):
        base_x          = self.base_x
        base_y          = self.base_y
        #no need to check tetris base, it should never be collision with view table
        if dir == MOVE_DOWN:
            for i in range(0, len(tetris_tuple)):
                if self.actTetrisPanel.view_table[tetris_tuple[i][1] + base_y - 1][tetris_tuple[i][0] + base_x] == 1:
                    return True

        elif dir == MOVE_LEFT:
            for i in range(0, len(tetris_tuple)):
                if self.actTetrisPanel.view_table[tetris_tuple[i][1] + base_y][tetris_tuple[i][0] + base_x - 1] == 1:
                    return True

        elif dir == MOVE_RIGHT:
            for i in range(0, len(tetris_tuple)):
                if self.actTetrisPanel.view_table[tetris_tuple[i][1] + base_y][tetris_tuple[i][0] + base_x + 1] == 1:
                    return True

        else:
            for i in range(0, len(tetris_tuple)):
                try:
                    if self.actTetrisPanel.view_table[base_y + tetris_tuple[i][1]][base_x + tetris_tuple[i][0]] == 1:
                        return True
                except IndexError:
                    print base_x, base_y, tetris_tuple[i][0], tetris_tuple[i][1]

        return False
          
    def start_move(self, dir):    
        if dir == MOVE_DOWN:
            self.base_y -= 1
        elif dir == MOVE_LEFT:
            self.base_x -= 1
            SoundPlay(SOUND_MOVE)
        elif dir == MOVE_RIGHT:
            self.base_x += 1
            SoundPlay(SOUND_MOVE)
        else:
            logging.error("Invalid move type[%d]", dir)
            return
            
        logging.debug ("start_move dir[%s] base_x[%d] base_y[%d]", move_name[dir], self.base_x, self.base_y)
        self.draw()
                   
    def change_allowed(self):
        #check if the border of next tetris is in the activity size
        base_x_tmp = self.base_x
        base_y_tmp = self.base_y
        
        if self.base_x + self.next_border[BORDER_LEFT] < 0:
            self.base_x -= self.next_border[BORDER_LEFT]
            
        elif self.base_x + self.next_border[BORDER_RIGHT] > self.cols-1:
            self.base_x -= self.next_border[BORDER_RIGHT]
            
        elif self.base_y + self.next_border[BORDER_BOTTOM] < 0:
            self.base_y -= self.next_border[BORDER_BOTTOM]
            
        elif self.base_y + self.next_border[BORDER_TOP] > self.rows-1:
            self.base_y -= self.next_border[BORDER_TOP]
            
        # check if the tetris tuple of next tetris collision with view table
        if True == self.check_collision(self.next_tetris) or True == self.check_collision(self.barrier):
            self.base_x = base_x_tmp
            self.base_y = base_y_tmp
            return False
            
        return True
        
    def CancelEvent(self):
        if self.actMoveTimer != None:
            self.actMoveTimer.cancel()
            self.actMoveTimer = None
        
        if self.actChangeTimer != None:
            self.actChangeTimer.cancel()
            self.actChangeTimer = None
        
    
    def CreateTetris(self, block_idx=4, shape_idx=3):
        self.CancelEvent()
        self.base = self.init_base    
        self.get_tetris(block_idx, shape_idx)
        self.get_next_tetris()
        self.get_barrier()
        self.border         = self.get_border(self.block_idx, self.shape_idx)
        self.next_border    = self.get_border(self.block_idx, self.shape_idx+1)
        
        #
        if self.border[BORDER_TOP] > 0:
            self.base_y -= self.border[BORDER_TOP]
        
        if self.actTetrisPanel != None and True == self.check_collision(self.tetris):
            #print "Game Over"
            #self.canvas.clear()
            self.FallTimer.cancel()
            return False
                
        self.draw()
        #print ("新方块::", block_idx, shape_idx, self.border, self.next_border)
        return True
        
    def CreateRandomTetris(self, draw=False):
        self.base = self.init_base
        block_idx = randint(0, len(self.tetris_tuple) - 1)
        shape_idx = randint(0, len(self.tetris_tuple[block_idx]) - 1)
        self.CreateTetris(block_idx, shape_idx)
        self.draw(adjust=True)
    
    #获取某一个特定方块的tuple   例如(0,0),(1,0),(0,-1)  更新block shape索引
    def get_tetris(self, block_idx, shape_idx): 
        #超过当前方块最大形状索引时，默认取首个
        if shape_idx >= len(self.tetris_tuple[self.block_idx]):
            shape_idx = 0 
        self.block_idx = block_idx
        self.shape_idx = shape_idx        
        self.tetris = self.tetris_tuple[block_idx][shape_idx]

    #获取某一个特定方块的下一个tuple   例如(0,0),(1,0),(0,-1)  不更新block shape索引
    def get_next_tetris(self):
        shape_idx = self.shape_idx  #由于每获取一个当前的方块时，都会自动获取下一个方块的tuple，这里shape_idx不能更新
        if shape_idx >= len(self.tetris_tuple[self.block_idx]) - 1:
            shape_idx = 0
        else:
            shape_idx += 1
        self.next_tetris = self.tetris_tuple[self.block_idx][shape_idx]
    
    #每个方块基于中心点 在其左右下上都有最大边界，用于判断其是否能左右上下移动
    #第1个是中心点(0,0)，border值从第2个开始遍历
    def get_border(self, block_idx, shape_idx):          
        border = [0, 0, 0, 0]
        
        #单点方块，tetris_tuple中第一个
        if len(self.tetris)==1:
            return border
        
        #获取方块最后一个形状的下一个方块border时，循环获取第一个即可
        if shape_idx >= len(self.tetris_tuple[self.block_idx]):
            shape_idx = 0
        
        #print "get_border::block_idx, shape_idx, tmp_shape_idx self.tetris len(self.tetris):", block_idx, shape_idx, tmp_shape_idx, self.tetris, len(self.tetris)
        tetrisTuple = self.tetris_tuple[block_idx][shape_idx]  
        for i in range(1, len(self.tetris)):
            border_x = tetrisTuple[i][0]
            border_y = tetrisTuple[i][1]
            if border_x < 0 and border_x < border[BORDER_LEFT]:  #left
                border[BORDER_LEFT] = border_x
            elif border_x > 0 and border_x > border[BORDER_RIGHT]: #right
                border[BORDER_RIGHT] = border_x

            if border_y < 0 and border_y < border[BORDER_BOTTOM]:  #down
                border[BORDER_BOTTOM] = border_y
            elif border_y > 0 and border_y > border[BORDER_TOP] : #top
                border[BORDER_TOP] = border_y
        
        print "border, block_idx, shape_idx", border, block_idx, shape_idx
        return border
        
    #获取方块到下一个方块需要经过的结点（相对中心点位置）
    #就像方块变形的障碍物，这些点对应的viewTable值为1，表示已有方块，不能变形
    def get_barrier(self):
        print "tetris_barrier len::", len(self.tetris_barrier[0])
        if len(self.tetris_barrier[self.block_idx]) == 1:
            self.barrier = self.tetris_barrier[self.block_idx][0]
        else:
            self.barrier = self.tetris_barrier[self.block_idx][self.shape_idx]

    def adjust_tetris_base(self):
        '''
        adjust the base to ensure the tetris only shown in the activity size
        :return:
        '''
        if self.base_x + self.border[0] < 0:
            self.base_x = -self.border[0]
        elif self.base_x + self.border[1] > self.cols-1:
            self.base_x = self.cols-1-self.border[1]

        if self.base_y + self.border[2] < 0:
            self.base_y = -self.border[2]
        elif self.base_y + self.border[3]>self.rows-1:
            self.base_y = self.rows-1-self.border[3]
    
    def draw(self, adjust=False):
        with self.canvas:
            self.canvas.clear()
            setColor(COLOR_DIC['BLACK'])

            print self.pos, self.base, self.init_base
            if adjust == True:
                self.adjust_tetris_base()

            #正方形边框
            Line(rectangle=[self.x + self.base_x * self.size_width + border_len, \
                            self.y + self.base_y * self.size_height + border_len, \
                            outline_rect_len, outline_rect_len], width=2)
            #实心方块
            Rectangle(pos=(self.x + self.base_x * self.size_width + border_len + rect_border_len, \
                           self.y + self.base_y * self.size_height + border_len + rect_border_len), \
                      size=(inner_rect_len, inner_rect_len))

            for i in range(1, len(self.tetris)):
                Line(rectangle=[self.x + (self.base_x+self.tetris[i][0]) * self.size_width + border_len, \
                                                     self.y + (self.base_y+self.tetris[i][1]) * self.size_height + border_len, \
                                                     outline_rect_len, outline_rect_len], width=2)

                Rectangle(pos=(self.x + (self.base_x+self.tetris[i][0]) * self.size_width + border_len + rect_border_len, \
                                   self.y + (self.base_y+self.tetris[i][1]) * self.size_height + border_len + rect_border_len), \
                                   size=(inner_rect_len, inner_rect_len))
        
#创建一个tetris，负责判断是否可以下降变形，然后调用tetris的相关操作
class TetrisArea(Widget):
    view_table = ListProperty([])

    #当前方块活动区域单元方块的大小
    size_width      = NumericProperty(0)
    size_height     = NumericProperty(0)
    tetris_size     = ReferenceListProperty(size_width, size_height)

    #当前活动方块的中心点在活动区域的偏移位置（活动区域的左下角为（0，0））
    base_x = NumericProperty(0)
    base_y = NumericProperty(0)
    base = ReferenceListProperty(base_x, base_y)

    start_base_x = NumericProperty(0)
    start_base_y = NumericProperty(0)
    init_base = ReferenceListProperty(start_base_x, start_base_y)

    #当前活动区域的列数与行数
    cols = NumericProperty(0)
    rows = NumericProperty(0)  #最大行
    activity_size = ReferenceListProperty(cols, rows)

    currTetris = ObjectProperty(None)
    nextTetrisObj = ObjectProperty(None)
    recordPanel   = ObjectProperty(None)
    pause = 0
    
    def __init__(self, **kwargs):
        super(TetrisArea, self).__init__(**kwargs)
        self.view_table = []
        self.total_cancel    = 0
        self.level           = 1
        self.scores          = 0
        self.timerEevent     = None
        self.timer_interval     = 3.0
        self.quicken   = False
    
    def ViewTableInit(self):
        if 0 == len(self.view_table):
            # to avoid override view_table, just expand it but no draw it.
            # so no need to adjust tetris base and only check it.
            self.view_table = [None] * (self.rows+2)
            for i in range(self.rows+2):
                self.view_table[i] = [0] * self.cols
            print "self.view_talbe", self.view_table

        self.downToEnd = True  
    
    def RefreshTetrisView(self):
        self.update_viewtable()
        self.fresh_tetris_view()
        
    def update_viewtable(self):
        activityTetris = self.currTetris
        tetrisTuple    = activityTetris.tetris
        base_x          = activityTetris.base_x
        base_y          = activityTetris.base_y
        border          = activityTetris.border
        cancel          = 0
        print "before update_viewtable", tetrisTuple
        try:
            self.view_table[base_y][base_x] = 1
            print "updtae view table be set to 1:", base_y, base_x
        except IndexError:
            print "self.base_y, self.base_x", base_y, base_x
        else:
            pass
            
        for i in range(0, len(tetrisTuple)):
            print "#####:", i, tetrisTuple[i][1]+base_y, tetrisTuple[i][0]+base_x
            self.view_table[tetrisTuple[i][1]+base_y][tetrisTuple[i][0]+base_x] = 1

        print "after update_viewtable", self.view_table
        start_idx   = base_y+border[2]
        end_idx     = base_y+border[3]
        
        for i in range(end_idx, start_idx-1, -1):
            count = 0
            try:
                for j in range(0, len(self.view_table[i])):#row
                    try:
                        if self.view_table[i][j] == 0:#row
                            break
                        else:
                            count += 1
                    except IndexError:
                        print "i,j", i, j
                        
                #print "i start_idx end_idx", i, start_idx, end_idx, count
                if count == len(self.view_table[i]):  #if current row is full of 1, it should be cancelled
                    del self.view_table[i]
                    bak_view_table = [0]*self.cols
                    self.view_table.append(bak_view_table)
                    cancel += 1

            except IndexError:
                    print "i",i      
        
        if cancel != 0:
            self.update_game_properities(cancel)
            SoundPlay(SOUND_CANCEL)
            print "after cancel update_viewtable", self.view_table
  
    def fresh_tetris_view(self):
        with self.canvas:
            self.canvas.clear()
            setColor(COLOR_DIC['BLACK'])
            if len(self.view_table) == 0:
                return

            for i in range(0, self.cols):
                for j in range(0, self.rows):
                    if self.view_table[j][i] == 1:
                        Line(rectangle=[self.x + i * outline_width + border_len, self.y + j * outline_width + border_len, \
                                       outline_rect_len, outline_rect_len], width=2)
                        Rectangle(pos=(self.x + i * outline_width + border_len + rect_border_len, \
                                       self.y + j * outline_width + border_len + rect_border_len), \
                                       size=(inner_rect_len, inner_rect_len))

    def update_game_properities(self, cancel):
        score = GetScores(cancel, self.level)
        self.scores += score
        
        self.total_cancel += cancel
        if self.total_cancel > 5*(self.level+1):
            self.level += 1
            logging.debug("Level upgrade to[%d], cancel[%d]", self.level, self.total_cancel)
            self.currTetris.UpgradeLevel()
            
        self.recordPanel.RecordUpdate(self.scores, self.level)
    
    def drawBackground(self):
        with self.canvas:
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    setColor(COLOR_DIC['GRAY'])
                    drawTetrisUnit(self.x, self.y, i, j)
    
    def DrawTimer(self):
        self.TimeEvent = Clock.schedule_interval(self.DrawUnit, 1.0/10)
        
    def DrawUnit(self, dt):
        print "start to draw gameover::", time.time()
        with self.canvas:
            setColor(COLOR_DIC['BLACK'])
            for i in range(self.rows-1, -1, -1):
                if self.view_table[i][0] == 1:
                    continue
                
                for j in range(0, self.cols):
                    self.view_table[i][j]=1
                    drawTetrisUnit(self.x, self.y, i, j)
            
                if i==0:
                    self.TimeEvent.cancel()
                else:
                    print "current rows:", i
                    break
                    
    def GameOver(self):
        for i in range(0, self.rows):
            for j in range(0, self.cols):
                self.view_table[i][j] = 0
              
        self.DrawTimer()                          
                    
def drawTetrisUnit(x, y, row_idx, col_idx):
    Line(rectangle=[x+col_idx*outline_width+border_len, y+row_idx*outline_width+border_len, \
                                    outline_rect_len, outline_rect_len], width=2)
                                    
    Rectangle(pos=(x+col_idx*outline_width+border_len+rect_border_len, \
                                   y+row_idx*outline_width+border_len+rect_border_len), \
                              size=(inner_rect_len, inner_rect_len))


#通过Boxlayout实现 图片与文字共存，同时绑定声音
class ImageLabel(ButtonBehavior, BoxLayout):
    image = ObjectProperty(None)

    image_source    = StringProperty("")
    label_text      = StringProperty("")
    sound_source    = StringProperty("")

    # def __init__(self, **kwargs):
    #     super(ImageLabel, self).__init__(**kwargs)
    def load_sound(self, sound_source):
        #sound_dir = os.path.join(os.path.abspath("./"), "data/sounds/")

        self.sound_fn = os.path.join("./data/sounds/", sound_source)
        if os.path.isfile(self.sound_fn):
            self.sound = SoundLoader.load(self.sound_fn)

    def play_sound(self):
        if self.sound_source != "":
            self.load_sound(self.sound_source)
            self.sound.play()
        #if self.sound_fn is not None:

    def on_press(self):
        self.image.color = [0.5, 0.5, 1, 1]
        self.play_sound()

    def on_release(self):
        self.image.color = [1, 1, 1, 1]
        pass


class TextImage(Label, Image):
    def __init__(self, **kwargs):
        super(TextImage, self).__init__(**kwargs)
        #self.text = "hello world"

class CtrlButtonImage(ButtonBehavior, Image):
#class CtrlButtonImage(Button):
    source = StringProperty("")

    def __init__(self, **kwargs):
        super(CtrlButtonImage, self).__init__(**kwargs)
        self.allow_stretch = True
        #self.texture = Texture.create(size=(640, 480), colorfmt='rgba')

        #self.source = '../data/images/info.png'
    def on_press(self):
        self.color = [1, 1, 0, 1]

    def on_release(self):
        self.color = [1, 1, 1, 1]

class CtrlButton(Button):

    def __init__(self, **kwargs):
        super(CtrlButton, self).__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 0)

class RecordPanelWidget(Widget):
    label_score = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(RecordPanelWidget, self).__init__(**kwargs)
        self.highest_score = 0
        self.level = 1
        self.score = 0
        #self.label_score.text = "123"

        with self.canvas:
            Color(1, 1, 1)
    
    def RecordPanelInit(self):
        self.label_score.text = '0'
        self.label_level.text = '1'
        
        try:
            fp = open('record.ini')
        except IOError:
            logging.error("open record.ini error")
        else:
            score = fp.readline()
            self.label_highest_score.text = score
            self.highest_score = int(score)
            logging.debug("Highest score is [%d]", self.highest_score)
            fp.close()
    
    def RecordUpdate(self, score, level):
        self.label_score.text = str(score)
        self.label_level.text = str(level)
        
        if score > self.highest_score:
            self.SaveHighestRecord(score)
        
    def SaveHighestRecord(self, score):
        try:
            fp = open('record.ini', 'w')
        except IOError:
            logging.error("open record.ini error")
        else:
            fp.write(str(score))
            self.highest_score = score
            fp.close()
            
class RootWidget(Widget):
    actTetrisBackgroundPanel        = ObjectProperty(None)
    nextTetrisBackgroundPanel       = ObjectProperty(None)
    actTetrisPanel                  = ObjectProperty(None)
    nextTetris                      = ObjectProperty(None)
     
    currTetris                      = ObjectProperty(None)
    
    ctrlPanel                       = ObjectProperty(None)
    recordPanel                     = ObjectProperty(None)
    anchor_x                        = NumericProperty(0)
    anchor_y                        = NumericProperty(0)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.game_start = False
        self.actTetrisBackgroundPanel.drawBackground()
        self.nextTetris.CreateRandomTetris()


    def wait_game_start(self):
        pass

    def StartGame(self):
        print "pos info", self.pos, self.size, self.center_x, self.center_y, self.width, self.height
        self.actTetrisBackgroundPanel.drawBackground()
        #self.nextTetrisBackgroundPanel.drawBackground()
        
        #为方块活动区域创建view_table
        self.actTetrisPanel.ViewTableInit()
        
        #创建下一个方块，也就是游戏的起始方块
        self.nextTetris.CreateRandomTetris()
        
        self.currTetris.actTetrisPanel          = self.actTetrisPanel
        self.currTetris.CreateRandomTetris()
        
        self.currTetris.nextTetrisObj           = self.nextTetris
        #
        self.actTetrisPanel.recordPanel         = self.recordPanel
        self.actTetrisPanel.currTetris          = self.currTetris
        
        self.recordPanel.RecordPanelInit()
        
        self.currTetris.StartTimer()
        
class TetrisApp(App):
    def build_config(self, config):
        config.setdefaults(
            'tetris',
            {
                "length": 50,
                "boader": 12,
                "activity_cols": 12,
                "activity_rows": 24
            }
        )

        config.setdefaults(
            'color',
            {
                "root_bgclr": "'0.6, 0.6, 0.6'"
            }
        )

    def build(self):
        #self.config = Config.get_configparser('app')
        self.config = ConfigParser(name='tetris_cfg')
        self.config.read('tetris.ini')
        #print "app cfg", self.config.filename

        #parser = ConfigParser.get_configparser('app')
        #clr = parser.get("color", "root_bgclr").encode("utf-8")
        clr = self.config.getdefault("color", "root_bgclr", '1,1,1')
        m = re.search(r'.*?(\d+).*,.*?(\d+).*,.*?(\d+).*', clr)
        self.root_bgclr_r = float(m.groups()[0])/255
        self.root_bgclr_g = float(m.groups()[1])/255
        self.root_bgclr_b = float(m.groups()[2])/255

        clr = self.config.getdefault("color", "activity_bgclr", '1,1,1')
        m = re.search(r'.*?(\d+).*,.*?(\d+).*,.*?(\d+).*', clr)
        self.activity_bgclr_r = float(m.groups()[0])/255
        self.activity_bgclr_g = float(m.groups()[1])/255
        self.activity_bgclr_b = float(m.groups()[2])/255

        # self.length = parser.getint("tetris", "length")
        # self.activity_rows = parser.getint("tetris", "activity_rows")
        # self.activity_cols = parser.getint("tetris", "activity_cols")
        self.anchor_x = self.config.getdefaultint("tetris", "anchor_x", 50)
        self.anchor_y = self.config.getdefaultint("tetris", "anchor_y", 50)
        self.length = self.config.getdefaultint("tetris", "length", 50)
        self.activity_rows = self.config.getdefaultint("tetris", "activity_rows", 24)
        self.activity_cols = self.config.getdefaultint("tetris", "activity_cols", 12)
        self.test = self.config.getdefaultint("tetris", "test", 100)
        logging.debug("[%d] [%d] [%d] [%d]", self.length, self.activity_rows, self.activity_cols, self.test)

        rootWidget = RootWidget()
        rootWidget.StartGame()
        return rootWidget
        
    def clear_canvas(self, obj):
        self.painter.canvas.clear()
        
if __name__ == '__main__':
    TetrisApp().run()
    