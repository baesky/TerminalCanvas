from .baeshade import BaeTermDrawPipeline, ColorPallette4bit
from .baeshadeutil import BaeshadeUtil
import time
from typing import Optional, Callable
import signal
import asyncio
from multiprocessing import Process
import sys

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

class BaePerfData:
    def __init__(self):
        self.logicTickTime = 0 # logic tick elapsed time
        self.encodingRTTime = 0 # encode times
        self.drawTime = 0 #scene drawing time, include encoding RT Time
        self.expectFPS = 0 # expected FPS
        self.frameTime = 0 # single frame delta time


class BaeApp:
    def __init__(self,render:BaeTermDrawPipeline = None,tick:Callable[[float],None]=None):
        
        self._FixedFps = 24
        self._displayRate = 1.0/self._FixedFps
        self._bExit = False
        self._tick = self.__tick if tick is None else tick
        self._frameTimer = None
        self._tickTimer = None
        
        self._perfData = BaePerfData()
        self._perfData.expectFPS = self._FixedFps

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
        self._renderPipe.shutDown()

    def __prepareRunApp(self):

        # enter exclusive mode
        self._renderPipe.useExclusiveScreen(True)

        self._frameTimer = BaeshadeUtil.Stopwatch()
        self._tickTimer = BaeshadeUtil.Stopwatch()

        #debug use
        self._tempPerf = BaeshadeUtil.Stopwatch()

    def __HandleCtrlZ(self,sig,frame):
        print('pressed ctrl+z')
        self.requestExit()

    @property
    def LimitFPS(self):
        return self._FixedFps


    async def __Loop(self):
        
        delta = self._frameTimer.last()
        self._perfData.frameTime = delta * 1000 # last frame time

        waitTimeSec = max(0.0,self._displayRate - delta)
        delayTime = waitTimeSec
        # if delayTime > 0.005:
        #     self._tickTimer.reset()
        #     await asyncio.sleep(delayTime - 0.001)
        #     delayTime -= self._tickTimer.stop()
        
        while delayTime > 0:
            self._tickTimer.reset()
            await asyncio.sleep(0.001)
            delayTime -= self._tickTimer.stop()

        

        self._tickTimer.reset()
        self._tick(delta + waitTimeSec)
        self._perfData.logicTickTime = self._tickTimer.stop() * 1000

        self._tickTimer.reset()
        await self._renderPipe.present(delta)
        self._perfData.drawTime = self._tickTimer.stop() * 1000

        # draw perf stat
        self._renderPipe.submitPerfData(self._perfData)


    async def __LoopWrapper(self):
        while self._bExit is False:
            await self.__Loop()
            #await asyncio.sleep(0.001)
    
    def __initLoop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__LoopWrapper())

    def run(self):
        try:
            self.__prepareRunApp()
            self.__initLoop()
        except KeyboardInterrupt:
            print('Key Interrupt! exit app!')
        except Exception as e:
            print(f'occur exception: {e}')
        finally:
            print('exit terminal canvas ...')
            self.__exitApp()
            sys.exit(0)
            




