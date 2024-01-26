from .baeshade import BaeTermDrawPipeline
from .baeshadeutil import BaeshadeUtil
import time
from typing import Optional, Callable
import signal
import asyncio
from multiprocessing import Process

class BaeKeyboard:
    def  __init__(self, keypress=None, keyrelease=None):
        self._keypress = keypress
        self._keyrelease = keyrelease
    
    @property
    def KeyPress(self):
        return self._keypress
    
    @property
    def KeyRelease(self):
        return self._keyrelease

class BaeApp:
    def __init__(self,render:BaeTermDrawPipeline = None,tick:Callable[[float],None]=None):
        
        self._FixedFps = 10
        self._displayRate = 1.0/self._FixedFps
        self._bExit = False
        self._tick = self.__tick if tick is None else tick
        self._frameTimer = None
        self._tickTimer = None
        self._tickPerf = 0

        self.attachRender(render)

        #handle ctrl+z
        signal.signal(signal.SIGTSTP, self.__HandleCtrlZ)

    async def __tick(self,delta:float):
        pass

    def attachRender(self, render:BaeTermDrawPipeline):
        self._renderPipe = render

    def requestExit(self):
         self._bExit = True

    def __exitApp(self):
        # back to previous terminal mode
        self._renderPipe.useExclusiveScreen(False)
        BaeshadeUtil.restoreScreen()

    def __prepareRunApp(self):

        # enter exclusive mode
        self._renderPipe.useExclusiveScreen(True)

        self._frameTimer = BaeshadeUtil.Stopwatch()
        self._tickTimer = BaeshadeUtil.Stopwatch()

    def __HandleCtrlZ(self):
        self.__exitApp()

    @property
    def LimitFPS(self):
        return self._FixedFps


    async def __Loop(self):
        delta = self._frameTimer.last()
        waitTimeSec = max(0.0,self._displayRate - delta)
        delayTime = waitTimeSec
        if delayTime > 0.005:
            time.sleep(delayTime - 0.002)
            delayTime -= self._frameTimer.last()
        
        while delayTime > 0:
            time.sleep(0)
            delayTime -= self._frameTimer.last()

        tickPerf = self._tickTimer.reset()
        self._tick(delta + waitTimeSec)
        self._tickPerf = self._tickTimer.stop()

        drawPerf = self._tickTimer.reset()
        await self._renderPipe.present(delta)
        drawPerf = self._tickTimer.stop()

        # draw perf stat
        self._renderPipe.drawText(1,self._renderPipe.backbufferHeight//2-1, 'tick: %.3f ms, draw: %.3f ms'%(self._tickPerf*1000.0, drawPerf*1000.0))
        self._renderPipe.drawText(1, self._renderPipe.backbufferHeight//2,'fixed fps:%d, bandwidth:%d' % (self.LimitFPS , self._renderPipe.strPerf))


    async def __LoopWrapper(self):
        try:
            while self._bExit is False:
                await self.__Loop()
        
            self.__exitApp()

        except KeyboardInterrupt:
            self.__exitApp()
    
    def __initLoop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__LoopWrapper())

    def run(self):        
        self.__prepareRunApp()
        #p = Process(target=self.__initLoop)
        #p.start()
        self.__initLoop()




