import os
import datetime
from time import sleep
from .baeshadeutil import BaeVec2d
from .baeshadeutil import BaeVec3d

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
    def RGB(r,g,b):
        r = max(0, min(255,r))
        g = max(0, min(255,g))
        b = max(0, min(255,b))
        return 16 + int(r/255 * 5) * 36 + int(g/255 * 5) * 6 + int(b/255 * 5) 

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

class Buffer:
    """
    back buffer for drawing
    """
    def __init__(self,w,h):
        self._size = BaeVec2d(w,h)


    @property
    def width(self):
        return self._size.X
    
    def reset(self,x,y):
        self._size = BaeVec2d(x,y)

    @property
    def height(self):
        return self._size.Y
    
    @property
    def Size(self):
        return self._size


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

# default buf
buf = Buffer(32,32)

def setBuffer(x,y,bClip = True):
    """
    set the buffer size you want to display in terminal, if not set, default value will be used.

    x: buffer width
    y: buffer height
    bClip: wether or not clip the size if value greater than terminal display size
    """
    bh,bw=os.popen('stty size', 'r').read().split()
    if bClip == True:
        buf.reset(max(0,min(x, int(bw))), max(0,min(y, int(bh))))
        if x>int(bw) or y>int(bh):
            print('Your termianl size is %s,%s, your input size is %d,%d, content may not display well...' % (bw,bh,x,y))
    else:
        buf.reset(x,y)

def presentation(clearColor = BaeVec3d(0,0,0), **kwargs):
    """
    call this to draw a frame
    clearColor: [r,g,b]
    shader: [optional] , if provided, will use shader routine instead of draw(), shader function must return a RGB()
    """

    shaderFunc = kwargs.get("shader", None)

    for row in range(buf.height):
        lum = clearColor
        for col in range(buf.width):
            if shaderFunc != None:
                lum = shaderFunc(col,row, buf)
            else: 
                for p in draw_list:
                    if p.x == col and p.y == row:
                        lum = p.color
                        break
                    else:
                        lum = clearColor
            nl = ""
            if col >= (buf.width - 1):
                nl = "\n"
            lum = ColorPallette8bit.RGB(lum.X,lum.Y,lum.Z)
            print('\x1b[48;5;%dm' % (lum) + " " + '\x1b[0m', end=nl)
           

