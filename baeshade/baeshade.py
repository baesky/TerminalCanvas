import os
import datetime
import asyncio
from .baeshademath import BaeVec2d
from .baeshademath import BaeVec3d
from .baeshademath import BaeMathUtil
from .baeshadeutil import BaeshadeUtil
from .baeshademath import BaeBoundingBox2D
from typing import Optional, Callable
from enum import Enum
from operator import itemgetter
from itertools import groupby


BAECODEX = BaeshadeUtil.EncodeTable

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
    
    def __init__(self,w:int,h:int,mode:BaeColorMode=BaeColorMode.Color8Bits,trimColor:BaeVec3d=BaeVec3d(0.0,0.0,0.0)):
        """
        w:terminal canvas width
        h:terminal canvas height
        """
        # row and colume in terminal
        self._termSize = BaeVec2d(w,BaeMathUtil.round(h/2))
        # virtual buffer size
        self._vSize = BaeVec2d(w,h)
        self._colormode = mode
        self._virtualBuffer = [ [BaeVec3d() for x in range(w)] for y in range(h)]
        self._cache = None
        self._cacheEx = None
        self._bDirt = False
        self._dirtRows = None
        self._effectiveRows = None
        self._invalidColor = trimColor

    def getVirtualBuffer(self):
        return self._virtualBuffer
    
    @property
    def virtualBuffer(self):
        return self._virtualBuffer
    
    def getPixel(self,x:int,y:int):
        return self._virtualBuffer[y][x]

    def getEffectPixel(self,x:int,y:int):
        test_color = self._virtualBuffer[y][x]
        return test_color if test_color != self._invalidColor else None

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

    @property
    def isValid(self) -> bool:
        return self._bDirt == False

    def fillAt(self,x:int,y:int,color:BaeVec3d)->None:
        """
        set RGB color to specified position
        """
        self._virtualBuffer[y][x] = color
        self._bDirt = True

    def __genEncode(self):
        """
        Encode colors to ANSI strings
        """
        self._cache = BaeTermDraw.encodeBuffer(self)
        self._bDirt = False
        return self._cache
    
    def getDirtRow(self):
        if self._dirtRows is not None:
            return self._dirtRows
        else:
            self.__genDirtRow(self._invalidColor)
            return self._dirtRows
    
    def __genDirtRow(self, ignoreColor:BaeVec3d):
        self._dirtRows = [set() for _ in range(self.pyhicalSize.Y)]
        for y in range(self.virtualSize.Y):
            for x in range(self.virtualSize.X):
                colr = self.getPixel(x,y)
                if colr != ignoreColor :
                    #dirt rt, must update 2 vertical subpixel once
                    self._dirtRows[y//2].add(x)
        #sort set
        self._dirtRows = map(sorted, self._dirtRows)

    def getEncodeBuffer(self)->str:
        if self.isValid is False:
            self.__genEncode()
        
        return self.cache
    
    def genEffectiveEncodeBuffer(self):
        self._cacheEx = [list(tuple()) for _ in range(self.pyhicalSize.Y)]
        for idx, rowSets in enumerate(self.getEffectivePixels()):
            for xpos,lenth in rowSets:
                self._cacheEx[idx].append( (xpos,BaeTermDraw.encodeBatchPixels(idx*2,xpos,lenth,self)))

        return self._cacheEx

    def getEncodeBufferEx(self):
        if self._cacheEx is None:
            return self.genEffectiveEncodeBuffer()
        else:
            return self._cacheEx

    @property
    def cache(self):
        return self._cache

    def getEffectivePixels(self):
        return self._effectiveRows if self._effectiveRows != None else self.__trim(self._invalidColor)

    def __trim(self, invalidColor:BaeVec3d):
        """
        return a list of tuple(start,length), start: dirt pixel x pos, length 
        rows in list are combined by 2 virtual row
        """

        self._effectiveRows = [list() for _ in range(self.pyhicalSize.Y)]
        for idx,row in enumerate(self.getDirtRow()):
            if len(row) == 0:
                continue
            for k, g in groupby(enumerate(row), lambda x:x[0]-x[1]):
                grp = (map(itemgetter(1),g))
                grp = list(map(int,grp))
                self._effectiveRows[idx].append((grp[0],grp[-1]-grp[0]+1))

        return self._effectiveRows

    def compute(self,kernel:Optional[Callable[[int,int, 'BaeBuffer'],BaeVec3d]]):
        """
        Run per pixel
        """
        if kernel == None:
            return

        bw = self.virtualSize.X
        bh = self.virtualSize.Y

        for row in range(bh):
            for col in range(bw):
                self.fillAt(col,row, kernel(col,row, BaeVec2d(bw,bh)))

class BaeSprite():
    def __init__(self,w:int,h:int,
                 cnt:int = 1,
                 fps:int=10,
                 mode:BaeColorMode=BaeColorMode.Color8Bits,
                 bgColr:BaeVec3d = BaeVec3d(0.0,0.0,0.0)):
        """
        w: width of sprite
        h: height of sprite
        cnt: sequence of the sprite
        fps: sprite playing speed
        mode: BaeColorMode
        """
        self._buff = [BaeBuffer(w,h,mode,bgColr) for i in range(cnt)]
        self._seqLen = cnt
        self._bgColor = bgColr
        self._playIndex = 0
        self._fps = fps
        self._bb = BaeBoundingBox2D()
        self._pos = BaeVec2d(0,0)

    @property
    def bgColor(self):
        return self._bgColor

    @property
    def Pos(self):
        return self._pos

    def setPos(self,x:int,y:int)->None:
        self._pos.SetX(x)
        self._pos.SetY(y)

    def rawFillPixel(self,x:int,y:int,color:BaeVec3d,seq:int=0)->None:
        self._buff[seq].fillAt(x, y, color)
        if color != self.bgColor:
            self._bb.addPoint(x,y)

    def seq(self,idx:int)->BaeBuffer:
        i = BaeMathUtil.clamp(idx, 0, self.seqNum - 1)
        return self._buff[i]

    @property
    def playIndex(self)->int:
        return BaeMathUtil.round(self._playIndex)

    def playAtRate(self, delta:float) -> BaeBuffer:
        self._playIndex = (self._playIndex + delta * self.fps) % self.seqNum

        return self.seq(self.playIndex)

    def resetFrame(self):
        self._playIndex = 0


    @property
    def fps(self):
        return self._fps

    @property
    def seqNum(self):
        return self._seqLen

class BaeTermDrawPipeline:
    def __init__(self, 
                 bufDesc,
                 bufNum:int = 2, # double buffer
                 debug = False):
        """
        bufDesc: {'width','height','colorMode'}
        """
        self._buff = None
        self._buffCount = bufNum
        self._backbuffer = [BaeBuffer(bufDesc['width'],bufDesc['height'],bufDesc['colorMode'])] * bufNum
        self._frameCounter = 0
        self._enableDebug = debug
        self._perfStrFlush = 0
        self.perfX = 0.0
        self._screenMode = False
        self._primList = [BaeSprite]


        self._backgroundCache:str = None
        self.bg = None

        self.bindRenderTaret(self._backbuffer[0], True)

    @property
    def isExclusiveMode(self):
        return self._screenMode

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
    def strPerf(self)->int:
        """
        character to flush in one frame
        """
        return self._perfStrFlush

    def useExclusiveScreen(self,bExclusive:bool):
        """
        true enter alternative screen
        false back to main screen
        """
        self._screenMode = bExclusive
        BaeshadeUtil.clearScreen()
        BaeshadeUtil.ExclusiveScreen(bExclusive)
        BaeshadeUtil.showCursor(bExclusive == False)
        if bExclusive == False:
            BaeshadeUtil.resetCursorPos()

    def getBackBuffer(self):
        idx = self._frameCounter % self._buffCount
        return self._backbuffer[idx]

    def bindRenderTaret(self, buf : BaeBuffer, bNeedInvalidBuffer:bool = False):
        """
        bind a RT to draw
        """
        self._buff = buf

    def __flush(self, buffstr):
        #print(buffstr,flush=False)
        BaeshadeUtil.output(buffstr)
        self._perfStrFlush += len(buffstr)

    def addBackGround(self, prim:BaeSprite):
        bmp = prim.seq(0)
        self._backgroundCache = bmp.getEncodeBuffer()
        self.bg = bmp

    def addPrimtive(self, prim:BaeSprite):
        self._primList.append(prim)

    @property
    def PrimitivesNum(self):
        return len(self._primList)

    def __encodeDirtPixelsLine(self,x:int,y:int, buffstr:str,lx:int=0,ly:int=0):
        #top-left corner pos is (1,1)
        return '\x1b[%d;%dH%s'%((ly+y)//2 + 1,lx+x + 1,buffstr)

    def drawBackground_Immeditately(self):
        
        if self._backgroundCache:
            self.__flush(self._backgroundCache)

    def drawBackground(self):
        
        rt = self._buff
        bg_size = self.bg.virtualSize
        for x in range(bg_size.X):
            for y in range(bg_size.Y):
                rt.fillAt(x,y, self.bg.getPixel(x,y))

    def drawPrimitiveOnBg_Immediately(self, delta:float):
        # draw dynamic primitives, not need really write to backbuffer
        for p in self._primList:
            #now only support sprite
            if isinstance(p,BaeSprite):
                
                #get corresponding frame
                bmp = p.playAtRate(delta)
                #generate encode, don't need write to bg
                pos = p.Pos
                encode_buff = []

                exRow = bmp.getEncodeBufferEx()

                for offsetY, tuplist in enumerate(exRow):
                    for enc in tuplist:
                        x, s = enc
                        encode_buff.append(self.__encodeDirtPixelsLine(x,offsetY*2,s,pos.X,pos.Y))

                self.__flush(''.join(encode_buff))

    def drawPrimitiveOnBg(self, delta:float):
        #_buff as Backgournd, not need update
        renderTarget = self._buff
        rtH = renderTarget.virtualSize.Y
        rtW = renderTarget.virtualSize.X

        # draw dynamic primitives, not need really write to backbuffer
        for p in self._primList:
            #now only support sprite
            if isinstance(p,BaeSprite):
                #get corresponding frame
                bmp = p.playAtRate(delta)
                bmp_size = bmp.virtualSize
                #generate encode, don't need write to bg
                pos = p.Pos

                for x in range(bmp_size.X):
                    for y in range(bmp_size.Y):
                        col = bmp.getEffectPixel(x,y)
                        if col is not None:
                            renderTarget.fillAt(round(pos.X + x), round(pos.Y + y),col)



    def drawSprite(self, x:int,y:int,src:BaeBuffer):

        dirtRow = src.getDirtRow()
        if dirtRow:
            for idx,row in enumerate(dirtRow):
                if len(row) == 0:
                    continue
                sx = 0
                for offsetX in row:
                    if 0 < (sx+x) < self.backbufferWidth and 0 < (idx*2 + y) < self.backbufferHeight:
                        tc = src.getPixel(offsetX,idx*2)
                        bc = src.getPixel(offsetX,idx*2+1)
                        self.drawPixel(sx+x,idx*2 + y, tc)
                        self.drawPixel(sx+x,idx*2 + 1 + y, bc)
                        sx += 1


    def drawPrimitive(self, delta):
         renderTarget = self._buff
         for p in self._primList:
             if isinstance(p,BaeSprite):
                 bmp = p.playAtRate(delta)
                 pos = p.Pos
                 exRow = bmp.getDir
                 for idx, rowSets in enumerate(exRow):
                     for xpos,lenth in rowSets:
                        for x in range(lenth):
                            self.drawPixel(xpos+x, idx*2, bmp)
                        

    
    async def presentEX(self, delta=0.0):
        # draw per primitve, get dirt rect list

        # draw bg where not dirt
        pass

    async def present(self, delta=0.0):
        """
        output backbuffer to terminal
        """
        self._frameCounter += 1
        self._perfStrFlush = 0
        
        if self.isExclusiveMode is True:
            BaeshadeUtil.resetCursorPos()

        self.bindRenderTaret(self.getBackBuffer())

        # draw bg on virtual buffer
        self.drawBackground()
        # draw actors on virutal buffer
        
        self.drawPrimitiveOnBg(delta)
        
        # encode buffers and submit draw
        dbg_time = BaeshadeUtil.Stopwatch()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.encodeRT)
        
        self.perfX = dbg_time.stop()

    def encodeRT(self,delta=0.0):
        if self._buff.isValid is False:
            self.__flush(self._buff.getEncodeBuffer())            
        else:
            self.__flush(self._buff._cache)

    def clearScene(self,clrColor:BaeVec3d):
        """
        clear backbuffer to clrColor
        Note: low performance
        """
        for row in range(self.backbufferHeight):
            for col in range(self.backbufferWidth):
                self.drawPixel(col,row, clrColor)

    def __clampInBuffer(self,pt:BaeVec2d):
        return BaeVec2d(BaeMathUtil.round(BaeMathUtil.clamp(pt.X, 0, self.backbufferWidth)), BaeMathUtil.round(BaeMathUtil.clamp(pt.Y, 0, self.backbufferHeight)))

    def drawText(self, x:int,y:int, txt:str)->None:
        BaeshadeUtil.resetCursorPos(y,x)
        print(txt)

    def drawPixel(self,x:int,y:int,color:BaeVec3d)->None:
        self._buff.fillAt(x,y,color)

    def drawSolidCircle2D(self, center:BaeVec2d, r:float, color:BaeVec3d)->None:
        c = self.__clampInBuffer(center)
        bw = self.backbufferWidth
        bh = self.backbufferHeight
        for row in range(bh):
            for col in range(bw):
                dist = BaeVec2d(col,row) - c
                dist = BaeVec2d.Dot(dist,dist)
                if dist <= r*r:
                    self.drawPixel(col,row,color)

    def drawLine2D(self, start:BaeVec2d, end:BaeVec2d, color:BaeVec3d)->None:
        """
        draw a line segment
        start: where the line start
        end: where the line ends
        color: the line colors
        """
        
        #clamp to safe zone

        sx = BaeMathUtil.round(BaeMathUtil.clamp(start.X, 0, self.backbufferWidth))
        sy = BaeMathUtil.round(BaeMathUtil.clamp(start.Y, 0, self.backbufferHeight))

        ex = BaeMathUtil.round(BaeMathUtil.clamp(end.X, 0, self.backbufferWidth))
        ey = BaeMathUtil.round(BaeMathUtil.clamp(end.Y, 0, self.backbufferHeight))

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
            self.drawPixel(int(ptX),int(ptY),color)
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
        return BaeVec3d(BaeMathUtil.round(r),BaeMathUtil.round(g),BaeMathUtil.round(b))

    @staticmethod
    def encodePixel(topColr,botColr,mode):
        """
        one time encoding 2 virtual pixel
        """
        tc = BaeTermDraw.quantify(topColr)
        bc = BaeTermDraw.quantify(botColr)

        encode4bit = lambda t, b : '\x1b[%d;%dm▀' % (t,b+10) #+ '\x1b[0m'
        encode8bit = lambda t,b : '\x1b[48;5;%dm' % (b) + '\x1b[38;5;%dm▀' % (t) #+ '\x1b[0m'
        encode24bit = lambda t, b : '\x1b[48;2;%d;%d;%dm' % (b.X,b.Y,b.Z) + '\x1b[38;2;%d;%d;%dm▀' % (t.X,t.Y,t.Z) #+ '\x1b[0m'

        match mode:
            case BaeColorMode.Color4Bits:
                return encode4bit(ColorPallette4bit.encodeColor(tc.X,tc.Y,tc.Z),ColorPallette4bit.encodeColor(bc.X,bc.Y,bc.Z))
            case BaeColorMode.Color8Bits:
                return encode8bit(ColorPallette8bit.encodeColor(tc.X,tc.Y,tc.Z),ColorPallette8bit.encodeColor(bc.X,bc.Y,bc.Z))
            case BaeColorMode.Color24Bits:
                return encode24bit(tc,bc)
            case _:
                assert True, "Not supported Color mode"
                return ''

    @staticmethod
    def encodeBatchPixels(row:int,start:int,lenth:int,buff:BaeBuffer):
        """
        row: y pos
        start: x pos for start
        length: how many pixel pair will be encode
        """
        encodeBuff=[]

        for c in range(lenth):
            tColr = buff.getPixel(start+c,row)
            bColr = buff.getPixel(start+c,row+1)
            subPixels = BaeTermDraw.encodePixel(topColr=tColr,botColr=bColr,mode =buff.colorMode)
            encodeBuff.append(subPixels)
        
        return ''.join(encodeBuff)

    @staticmethod
    def encodeBuffer(buff:BaeBuffer):
        """
        encode buffer to ANSI Esc Code string list for presentation
        """
        w = buff.virtualSize.X
        h = buff.virtualSize.Y

        encodeBuff=[]

        for row in range(0,h,2):
            for col in range(w):
                nl = BAECODEX.NewLine if col >= (w - 1) else BAECODEX.Empty
                tColr = buff.getPixel(col,row)
                bColr = buff.getPixel(col,row+1)
                # draw per line so we can get debug with visualize
                subPixels = BaeTermDraw.encodePixel(topColr=tColr,botColr=bColr,mode =buff.colorMode)
                encodeBuff.append(subPixels + nl)

        return ''.join(encodeBuff)
    
