import os
import datetime
from time import sleep
from .baeshadeutil import BaeVec2d
from .baeshadeutil import BaeVec3d
from typing import Optional, Callable

# gray scale level
GRAYSCALELEN = 23

# gray scale index
GRAYSCALESTART = 232

class ColorPallette8bit:
    """
    ref to https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

    """
    def __init__(self):
        self._grayScale = []
        for i in range(GRAYSCALELEN):
            self._grayScale.append(GRAYSCALESTART+i)

        self._black = 0
        self._red = 1
        self._green = 2
        self._yellow = 3
        self._blue = 4
        self._magenta = 5
        self._cyan = 6
        self._white = 7

    """
    get gray scale color
    lum: the scale valid range [0,23], which mean from black to white
    """
    def getGrayScale(self,lum):
        assert 0 <= lum <= 23
        return self._grayScale[lum]


    """
    color space is a 6x6x6 cube
    r,g,b: valid value in [0,255]
    """
    @staticmethod
    def RGBIndex(r,g,b):
        return 16 + int(r/255.0 * 5) * 36 + int(g/255.0 * 5) * 6 + int(b/255.0 * 5) 

    @property
    def Black(self):
        return self._black
    
    @property
    def BrightBlack(self):
        return self._black + 8
    
    @property
    def Red(self):
        return self._red
    
    @property
    def BrightRed(self):
        return self._red + 8
    
    @property
    def Green(self):
        return self._green
    
    @property
    def BrightGreen(self):
        return self._green + 8
    
    @property
    def Yellow(self):
        return self._yellow
    
    @property
    def BrightYellow(self):
        return self._yellow + 8

    @property
    def Blue(self):
        return self._blue
    
    @property
    def BrightBlue(self):
        return self._blue + 8
    
    @property
    def Magenta(self):
        return self._magenta
    
    @property
    def BrightMagenta(self):
        return self._magenta + 8
    
    @property
    def Cyan(self):
        return self._cyan
    
    @property
    def BrightCyan(self):
        return self._cyan + 8
    
    @property
    def White(self):
        return self._white
    
    @property
    def BrightWhite(self):
        return self._white + 8


baeColorPallette = ColorPallette8bit()

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
    back buffer for drawing
    """
    def __init__(self,w,h,mode=BaeColorMode.Color8Bits):
        self._size = BaeVec2d(w,h)
        self._colormode = mode

    @property
    def colorMode(self):
        return self._colormode

    @property
    def width(self):
        return self._size.X

    @property
    def height(self):
        return self._size.Y
    
    @property
    def size(self):
        return self._size
    
    def reset(self,x,y,mode=BaeColorMode.Color8Bits):
        self._size = BaeVec2d(x,y)
        self._mode = mode

class BaeTermDrawPipeline:
    def __init__(self, 
                 buf:BaeBuffer, 
                 ps: Optional[Callable[[int,int, BaeBuffer],BaeVec3d]],
                 debug = False):
        """
        buf: render target
        ps: pixel shader
        """
        self._buff = buf
        self._ps = ps
        self._enableDebug = debug

    def getShader(self):
        return self._ps

    def getBuffer(self):
        return self._buff

    @property
    def getRTHeight(self):
        return self._buff.height
    
    @property
    def getRTWidth(self):
        return self._buff.width
    
    @property
    def getColorMode(self):
        return self._buff.colorMode

    def debugable(self):
        return self._enableDebug

    def bindRenderTaret(self, buf : BaeBuffer):
        """
        bind a RT to draw
        """
        self._buff = buf



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
    def encodeColor(rgb, mode):
        qc = BaeTermDraw.quantify(rgb)
        match mode:
            case BaeColorMode.Color8Bits:
                colorIdx = ColorPallette8bit.RGBIndex(qc.X,qc.Y,qc.Z)
                return '\x1b[48;5;%dm' % (colorIdx) + " " + '\x1b[0m'
            case BaeColorMode.Color24Bits:
                return '\x1b[48;2;%d;%d;%dm' % (qc.X,qc.Y,qc.Z) + " " + '\x1b[0m'
            case _:
                assert True, "you should use correct color mode"
                return '\x1b[31mError Color Mode!\x1b[0m'
    
    @staticmethod
    def encode(str, rgb, mode, fg=False):
        qc = BaeTermDraw.quantify(rgb)
        match mode:
            case BaeColorMode.Color8Bits:
                colorIdx = ColorPallette8bit.RGBIndex(qc.X,qc.Y,qc.Z)
                return '\x1b[48;5;%dm' % (colorIdx) + str + '\x1b[0m'
            case BaeColorMode.Color24Bits:
                return '\x1b[48;2;%d;%d;%dm' % (qc.X,qc.Y,qc.Z) + str + '\x1b[0m'
            case _:
                assert True, "you should use correct color mode"
                return '\x1b[31mError Color Mode!\x1b[0m'

    @staticmethod
    def present(pipeCfg : BaeTermDrawPipeline, clrCol = BaeVec3d(0,0,0), **kwargs):
        """
        call this to draw a frame
        pipeCfg: a BaeTermDrawPipeline to config how to draw
        clrCol: a BaeVec3d type
        """

        shaderFunc = pipeCfg.getShader()
        rt = pipeCfg.getBuffer()
        bDebugDraw = pipeCfg.debugable()
        tempBuffer = []

        for row in range(pipeCfg.getRTHeight):
            lum = clrCol
            for col in range(pipeCfg.getRTWidth):
                if shaderFunc != None:
                    lum = shaderFunc(col,row, rt)
                else: 
                    for p in draw_list:
                        if p.x == col and p.y == row:
                            lum = p.color
                            break
                        else:
                            lum = clrCol
                nl = ""
                if col >= (rt.width - 1):
                    nl = "\n"
                
                # draw per line so we can get debug with visualize
                if bDebugDraw == True:
                    print(BaeTermDraw.encode(" ",lum,pipeCfg.getColorMode), end=nl)
                else:
                    tempBuffer.append(BaeTermDraw.encode(" ",lum, pipeCfg.getColorMode) + nl)

        if bDebugDraw == False:
            print(''.join(tempBuffer))


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

