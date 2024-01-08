import os
import datetime
from time import sleep
from .baeshadeutil import BaeVec2d
from .baeshadeutil import BaeVec3d
from .baeshadeutil import BaeMathUtil
from typing import Optional, Callable
from enum import Enum


# gray scale level
GRAYSCALELEN = 23

# gray scale index
GRAYSCALESTART = 232

# ref to https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

class ColorPallette4bit(Enum):

    black = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37

    black_bg = black + 10
    red_bg = red + 10
    green_bg = green + 10
    yellow_bg = yellow + 10
    blue_bg = blue + 10
    magenta_bg = magenta + 10
    cyan_bg = cyan + 10
    white_bg = white + 10

    black_bright = 90
    red_bright = 91
    green_bright = 92
    yellow_bright = 93
    blue_bright = 94
    magenta_bright = 95
    cyan_bright = 96
    white_bright = 97

    black_bg_bright = 100
    red_bg_bright = 101
    green_bg_bright = 102
    yellow_bg_bright = 103
    blue_bg_bright = 104
    magenta_bg_bright = 105
    cyan_bg_bright = 106
    white_bg_bright = 107

    @staticmethod
    def encodeColor(r,g,b):
        cr = BaeMathUtil.clamp(r,0,1)
        cg = BaeMathUtil.clamp(g,0,1)
        cb = BaeMathUtil.clamp(b,0,1)
        
        cbit = cr << 2 | cg <<1 | cb

        match cbit:
            case 7:
                return ColorPallette4bit.white
            case 6:
                return ColorPallette4bit.yellow
            case 5:
                return ColorPallette4bit.magenta
            case 4:
                return ColorPallette4bit.red
            case 3:
                return ColorPallette4bit.cyan
            case 2:
                return ColorPallette4bit.green
            case 1:
                return ColorPallette4bit.blue
            case _:
                return ColorPallette4bit.black



    @staticmethod
    def grayscale(s):
        """
        s : 0-1 level gray scale, other values will be clamped
        """
        grayLv = BaeMathUtil.clamp(s,0,1)
        return ColorPallette4bit.black if grayLv == 0 else ColorPallette4bit.white

class ColorPallette8bit(Enum):

    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5
    cyan = 6
    white = 7

    black_bright = black + 8
    red_bright = red + 8
    green_bright = green + 8
    yellow_bright = yellow + 8
    blue_bright = blue + 8
    magenta_bright = magenta + 8
    cyan_bright = cyan + 8
    white_bright = white + 8

    @staticmethod
    def encodeColor(r,g,b):
        return 16 + int(r/255.0 * 5) * 36 + int(g/255.0 * 5) * 6 + int(b/255.0 * 5)
    
    @staticmethod
    def grayscale(s):
        """
        s : 0-23 level gray scale, other values will be clamped
        """
        grayLv = BaeMathUtil.clamp(s,0,23)
        return 232 + grayLv

class ColorPallette24bit(Enum):
    black = BaeVec3d(0,0,0)
    red = BaeVec3d(255,0,0)
    green = BaeVec3d(0,255,0)
    blue = BaeVec3d(0,0,255)
    yellow = BaeVec3d(255,255,0)
    magenta = BaeVec3d(255,0,255)
    cyan = BaeVec3d(0,255,255)
    white = BaeVec3d(255,255,255)
    
    @staticmethod
    def encodeColor(r,g,b):
        return BaeVec3d(r,g,b)
    
    @staticmethod
    def grayscale(s):
        """
        s : 0-255 level gray scale, other values will be clamped
        """
        grayLv = BaeMathUtil.clamp(s,0,255)
        return BaeVec3d(grayLv,grayLv,grayLv)

class BaeColorMode:

    @staticmethod
    def Color4Bits():
        """
        basic color for terminal, 8 basic color + 8 bright version
        not implement yet
        """
        return '4-bit'

    @staticmethod
    def Color8Bits():
        """
        256-color
        """
        return '8-bit'
    
    @staticmethod
    def Color24Bits():
        """
        True-color
        """
        return '24-bit'
    
class BaeBuffer:
    """
    virtual buffer for drawing
    """
    
    def __init__(self,w,h,mode=BaeColorMode.Color8Bits):
        """
        w:terminal canvas width
        h:terminal canvas height
        """
        # row and colume in terminal
        self._termSize = BaeVec2d(w,h)
        # virtual buffer size
        self._vSize = BaeVec2d(w,h * 2)
        self._colormode = mode
        self._virtualBuffer = [ [0 for x in range(w)] for y in range(h*2)]

    def getVirtualBuffer(self):
        return self._virtualBuffer
    
    @property
    def virtualBuffer(self):
        return self._virtualBuffer

    @property
    def colorMode(self):
        return self._colormode
    
    @property
    def virtualSize(self):
        """
        Terminal virutal area: one character contains 2 vertical subpixels
        """
        return self._vSize
    
    @property
    def pyhicalSize(self):
        """
        Terminal area: Rows multiplied by columns
        """
        return self._termSize


class BaeTermDrawPipeline:
    def __init__(self, 
                 buf:BaeBuffer, 
                 ps: Optional[Callable[[int,int, BaeBuffer],BaeVec3d]] = None,
                 debug = False):
        """
        buf: render target
        ps: pixel shader
        """
        self._buff = buf
        self._ps = ps
        self._enableDebug = debug

    @property
    def pixelShader(self):
        return self._ps

    @property
    def backbuffer(self):
        return self._buff.virtualBuffer
    
    @property
    def backbufferWidth(self):
        return self._buff.virtualSize.X
    
    @property
    def backbufferHeight(self):
        return self._buff.virtualSize.Y

    @property
    def colorMode(self):
        return self._buff.colorMode

    @property
    def debugable(self):
        return self._enableDebug

    def bindRenderTaret(self, buf : BaeBuffer):
        """
        bind a RT to draw
        """
        self._buff = buf

    def __getRT(self):
        return self._buff.getVirtualBuffer()

    def __draw(self):

        if self.pixelShader == None:
            return

        bw = self.backbufferWidth
        bh = self.backbufferHeight
        vBuf = self.__getRT()
        for row in range(bh):
            for col in range(bw):
                vBuf[row][col] = self.pixelShader(col,row, BaeVec2d(self.backbufferWidth,self.backbufferHeight))

    def present(self):

        self.__draw()

        tempBuffer=[]
        for row in range(0,self.backbufferHeight,2):
            for col in range(self.backbufferWidth):
                nl = "\n" if col >= (self.backbufferWidth - 1) else ""
                tColr = self.backbuffer[row][col]
                bColr = self.backbuffer[row+1][col]
                # draw per line so we can get debug with visualize
                pixelPair = BaeTermDraw.encodePixel(topColr=tColr,botColr=bColr,mode =self.colorMode)
                if self.debugable == True:
                    print(pixelPair, end=nl)
                else:
                    tempBuffer.append(pixelPair + nl)

        if self.debugable == False:
            print(''.join(tempBuffer),flush=True)

    def clearScene(self,clrColor:BaeVec3d):
        for row in range(self.backbufferHeight):
            for col in range(self.backbufferWidth):
                self.__getRT()[row][col] = clrColor

    def __clampInBuffer(self,pt:BaeVec2d):
        return BaeVec2d(round(BaeMathUtil.clamp(pt.X, 0, self.backbufferWidth)), round(BaeMathUtil.clamp(pt.Y, 0, self.backbufferHeight)))

    def drawCircle2D(self, center:BaeVec2d, r:float, color:BaeVec3d):
        c = self.__clampInBuffer(center)
        bw = self.backbufferWidth
        bh = self.backbufferHeight
        for row in range(bh):
            for col in range(bw):
                dist = BaeVec2d(col,row) - c
                dist = BaeVec2d.Dot(dist,dist)
                if dist <= r*r:
                    self.__getRT()[row][col] = color

    def drawLine2D(self, start:BaeVec2d, end:BaeVec2d, color:BaeVec3d):
        """
        draw a line segment
        start: where the line start
        end: where the line ends
        color: the line colors
        """
        
        #clamp to safe zone

        sx = round(BaeMathUtil.clamp(start.X, 0, self.backbufferWidth))
        sy = round(BaeMathUtil.clamp(start.Y, 0, self.backbufferHeight))

        ex = round(BaeMathUtil.clamp(end.X, 0, self.backbufferWidth))
        ey = round(BaeMathUtil.clamp(end.Y, 0, self.backbufferHeight))

        # simple DDA
        dx = ex - sx
        dy = ey - sy
        
        steps = abs(dx) if abs(dx) > abs(dy) else abs(dy)

        if steps == 0:
            return

        incX = dx / float(steps)
        incY = dy / float(steps)
        
        ptX = sx
        ptY = sy
        for x in range(steps):
            self.__getRT()[round(ptY)][round(ptX)] = color
            ptX += incX
            ptY += incY
            


class BaeTermDraw:

    @staticmethod
    def quantify(rgb : BaeVec3d):
        """
        make sure value in a safty range which terminal like
        """
        r = max(0, min(255,rgb.X))
        g = max(0, min(255,rgb.Y))
        b = max(0, min(255,rgb.Z))
        return BaeVec3d(round(r),round(g),round(b))

    @staticmethod
    def encodePixel(topColr,botColr,mode):
        """
        one time encoding 2 virtual pixel
        """
        tc = BaeTermDraw.quantify(topColr)
        bc = BaeTermDraw.quantify(botColr)

        encode4bit = lambda t, b : '\x1b[%d;%dm▀' % (t,b+10) + '\x1b[0m'
        encode8bit = lambda t,b : '\x1b[48;5;%d;%d;%dm' % (b.X,b.Y,b.Z) + '\x1b[38;5;%d;%d;%dm▀' % (t.X,t.Y,t.Z) + '\x1b[0m'
        encode24bit = lambda t, b : '\x1b[48;2;%d;%d;%dm' % (b.X,b.Y,b.Z) + '\x1b[38;2;%d;%d;%dm▀' % (t.X,t.Y,t.Z) + '\x1b[0m'

        match mode:
            case BaeColorMode.Color4Bits:
                return encode4bit(ColorPallette4bit.encodeColor(tc.X,tc.Y,tc.Z),ColorPallette4bit.encodeColor(bc.X,bc.Y,bc.Z))
            case BaeColorMode.Color8Bits:
                return encode4bit(ColorPallette8bit.encodeColor(tc.X,tc.Y,tc.Z),ColorPallette8bit.encodeColor(bc.X,bc.Y,bc.Z))
            case BaeColorMode.Color24Bits:
                return encode24bit(tc,bc)
            case _:
                assert True, "Not supported Color mode"
                return ''


class PixelCell:
    """
    data on particular location
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

draw_list = []
def drawPallette(x,y,color):
    """
    set a color on the location you specified
    x,y: where the color will shade on the buffer
    color: color pallette
    """
    draw_list.append(PixelCell(x,y,color))

