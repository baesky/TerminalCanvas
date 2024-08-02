import os
import datetime
import asyncio
import multiprocessing
import queue

from .baeshademath import BaeVec3d,BaeVec2d,BaeMathUtil,BaeBoundingBox2D
from .baeshadeutil import BaeshadeUtil

from typing import Optional, Callable
from enum import Enum
from operator import itemgetter
from itertools import groupby
import time

BAECODEX = BaeshadeUtil.EncodeTable

"""
core function for drawing
"""
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

class BaeFontStyle(Enum):
    normal = 0
    bold = 1
    italic = 3
    underline = 4

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

    def compute(self,kernel:Optional[Callable[[int,int, dict],BaeVec3d]]):
        """
        Run per pixel
        """
        if kernel == None:
            return

        bw = self.virtualSize.X
        bh = self.virtualSize.Y

        for row in range(bh):
            for col in range(bw):
                extra = {'time':time.time(),'bw':bw,'bh':bh}

                self.fillAt(col,row, kernel(col,row, extra))

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
        self._pos.X = x
        self._pos.Y = y

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

class BaeEncodeWorker():
    def __init__(self, func=None, args=()):
        self._worker = multiprocessing.Process(target=func, args=args)
    def run(self):
        self._worker.start()

    def stop(self):
        self._worker.terminate()
        self._worker.join()
    
class BaeWorkerPayload():
    def __init__(self, payload):
        self._payload = multiprocessing.Manager().dict()
        self._payload.update(payload)

    def getPayload(self):
        return self._payload
    
    def update(self, key, value):
        self._payload[key] = value

class BaeWorkQueue():
    def __init__(self, workSize:3):
        self._queue = multiprocessing.Manager().Queue(workSize)

    def getQueue(self):
        return self._queue

def BaeEncodingTask(payload):
    while True:
        
        if payload['bExclusive'] is True:
            BaeshadeUtil.resetCursorPos()

        encode = payload['rtQueue'].get()
        BaeTermDrawPipeline.draw(encode)

        perfData = payload['perfData'].get()
        if perfData.bShowPerf:
            perfStrFlush = len(encode)
            BaeTermDrawPipeline.drawStyleText(1, 1, f'fps:{perfData.expectFPS}/{1000 // perfData.frameTime}, Frame:{perfData.frameTime:.2f}, Logic:{perfData.logicTickTime:.2f},'
                                            f' Draw:{perfData.drawTime:.2f}, Encoding:{payload["_perfSubmitRT"]*1000:.2f}, bandwidth:{perfStrFlush:,}'
                                            f' \n'
                                            ,ColorPallette4bit.blue,ColorPallette4bit.black_bg)
        else:
            #BaeTermDrawPipeline.drawStyleText(1, 1, f'\n')
            BaeshadeUtil.resetCursorPos(2,1)
        
class BaeFrameCounter:
    def __init__(self):
        self._counter = 0

    def Increment(self):
        if self._counter > 9999999:
            self._counter = 0
        else:
            self._counter += 1
    def frame(self):
        return self._counter

class BaeRenderingTask:

    def setDPI(self, DPI:'BaeTermDrawPipeline'):
        self.__DPI = DPI

    @property
    def DPI(self):
        return self.__DPI

    def __call__(self, delta:float):
        if self.__DPI is not None:
            self.onDraw(delta)
        else:
            raise Exception("DPI not set")

    def onInit(self):
        pass

    def onDraw(self, delta:float):
        pass

class BaeTermDrawPipeline:
    def __init__(self, 
                 bufDesc,
                 ):
        """
        bufDesc: {'width','height','colorMode'}
        """
        self._buff = None
        self._buffCount = bufDesc.get('bufferCount',3)
        self._strictMode = bufDesc.get('bStrict',False)
        self._backbuffer = [BaeBuffer(bufDesc['width'],bufDesc['height'],bufDesc.get('colorMode', BaeColorMode.Color24Bits))] * self._buffCount

        self._frameCounter = BaeFrameCounter()

        self._screenMode = False
        self._primList = [BaeSprite]

        self._rtQueue = BaeWorkQueue(self._buffCount)
        self._perfData = BaeWorkQueue(self._buffCount)
        payload = {
            'rtQueue': self._rtQueue.getQueue(),
            'bExclusive': self.isExclusiveMode,
            'perfData': self._perfData.getQueue(),
            '_perfRenderingTask': 0,
        }
        self.workerPayload = BaeWorkerPayload(payload)
        self.encodeWorker = BaeEncodeWorker(BaeEncodingTask, (self.workerPayload.getPayload(),))
        self.encodeWorker.run()

        #bind a default rt
        self.__bindRenderTaret(self._backbuffer[0], True)


    def __del__(self):
        self.shutDown()

    def shutDown(self):
        if self.encodeWorker is not None:
            self.encodeWorker.stop()

    def runShader(self, shader:Callable[[int,int,dict],BaeVec3d]):
        self.__getBackBuffer().compute(shader)

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

    def submitRT(self, encodedData):
        """
        submit data to renering worker, if queue is full mean the term is busy, drop the data
        """
        try:
            if self._strictMode: 
                self._rtQueue.getQueue().put(encodedData)
            else:
                self._rtQueue.getQueue().put_nowait(encodedData)
        except (queue.Full, queue.Empty):
            pass

    
    def submitPerfData(self, perfData):
        try:
            if self._strictMode: 
                self._perfData.getQueue().put(perfData)
            else:
                self._perfData.getQueue().put_nowait(perfData)
        except (queue.Full, queue.Empty):
            pass

    def __getBackBuffer(self):
        idx = self._frameCounter.frame() % self._buffCount
        return self._backbuffer[idx]

    def __bindRenderTaret(self, buf : BaeBuffer, bNeedInvalidBuffer:bool = False):
        """
        bind a RT to draw
        """
        self._buff = buf

    @staticmethod
    def draw(buffstr:str)->None:
        """
        direct draw encoded data on backbuffer
        """
        if buffstr is not None:
            BaeshadeUtil.output(buffstr)

    def addPrimtive(self, prim:BaeSprite):
        self._primList.append(prim)

    @property
    def PrimitivesNum(self):
        return len(self._primList)

    def BatchDrawPrimitives(self, delta:float):
        return self.__drawPrimitive(delta)

    def __drawPrimitive(self, delta:float):
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

    async def present(self, delta=0.0, tasklist:Optional[list[BaeRenderingTask]]=None):
        """
        output backbuffer to terminal, internal use only
        """
        self._frameCounter.Increment()

        
        # bind current working backbuffer
        self.__bindRenderTaret(self.__getBackBuffer())


        # do rendering work
        perfWatch = BaeshadeUtil.Stopwatch()
        for work in tasklist:
            work(delta)

        self.workerPayload.update('_perfRenderingTask', perfWatch.stop())

        perfWatch.reset()
        # encode buffers and submit draw
        #if queue is full, wait here
        self.submitRT(self.__getBackBuffer().getEncodeBuffer())
        self.workerPayload.update('_perfSubmitRT', perfWatch.stop())



    def __encodeRT(self,delta=0.0):
        if self._buff.isValid is False:
            BaeTermDrawPipeline.draw(self._buff.getEncodeBuffer())            
        else:
            BaeTermDrawPipeline.draw(self._buff._cache)

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

    @staticmethod
    def drawText(x:int,y:int, txt:str)->None:
        BaeshadeUtil.resetCursorPos(y,x)
        print(txt)

    @staticmethod
    def drawStyleText(x:int, y:int, txt:str, fontColor=ColorPallette4bit.white, bgColor= ColorPallette4bit.black_bg, style:BaeFontStyle = 0, bNeedRestStyle:bool = False):
        # user responed for format like 'new line'
        encode = BaeTermDraw.encodeTextStyle(fontColor, bgColor, style)
        buildStr = f'{encode}{txt}{BaeTermDraw.encodeResetToken() if bNeedRestStyle else ""}'
        BaeshadeUtil.resetCursorPos(y,x)
        BaeTermDrawPipeline.draw(buildStr)


    def drawPixel(self,x:int,y:int,color:BaeVec3d)->None:
        """
        draw a pixel in terminal with color, note: performance is slow
        """
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
    def encodeResetToken():
        return '\x1b[0m'

    @staticmethod
    def encodeTextStyle(fontColor, bgColor, style:BaeFontStyle = 0)->str:
        encode4bit = lambda f,b : f'\x1b[{f}m\x1b[{b}m'
        encode8bit = lambda f,b: f'\x1b[48;5;{b}m\x1b[38;5;{f}m'
        encode24bit = lambda f,b : f'\x1b[48;2;{b.X};{b.Y};{b.Z}m\x1b[38;2;{f.X};{f.Y};{f.Z}m'

        styleEncode = f'\x1b[{style}m' if style !=0 else '' 
        if isinstance(fontColor, ColorPallette4bit):
            return styleEncode + encode4bit(fontColor.value, bgColor.value)
        elif isinstance(fontColor, ColorPallette8bit):
            return styleEncode + encode8bit(fontColor.value, bgColor.value)
        else:
            return styleEncode + encode24bit(fontColor, bgColor)

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
    
