from .baeshade import BaeTermDrawPipeline, ColorPallette4bit, BaeRenderingTask
from .baeshademath import BaeVec3d
from .baeshadeutil import BaeshadeUtil
import time
from typing import Optional, Callable
import signal
import asyncio
from multiprocessing import Process
import sys
import platform

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
        self.bShowPerf = False

class BaeApp:
    def __init__(self,renderDesc:dict,tick_func:Callable[[float],None]=None,bShowPerf=False):
        
        self._FixedFps = 24
        self._displayRate = 1.0/self._FixedFps
        self._bExit = False
        self._tick = self.__tick if tick_func is None else tick_func
        self._frameTimer = None
        self._tickTimer = None
        
        self._perfData = BaePerfData()
        self._perfData.expectFPS = self._FixedFps
        self._perfData.bShowPerf = bShowPerf

        self.attachRender(BaeTermDrawPipeline(renderDesc))

        if platform.system() != 'Windows':
            #handle ctrl+z
            signal.signal(signal.SIGTSTP, self.__HandleCtrlZ)

        self._renderingTask = []


    async def __tick(self,delta:float):
        pass

    def addTask(self, task:BaeRenderingTask):
        task.setDPI(self.__renderPipe)
        task.onInit()
        self._renderingTask.append(task)

    def attachRender(self, render:BaeTermDrawPipeline):
        self.__renderPipe = render

    def requestExit(self):
         self._bExit = True

    def __exitApp(self):
        # back to previous terminal mode
        self.__renderPipe.useExclusiveScreen(False)
        BaeshadeUtil.restoreScreen()
        self.__renderPipe.shutDown()

    def __prepareRunApp(self):

        # enter exclusive mode
        self.__renderPipe.useExclusiveScreen(True)

        self._frameTimer = BaeshadeUtil.Stopwatch()
        self._tickTimer = BaeshadeUtil.Stopwatch()


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
        
        while delayTime > 0:
            self._tickTimer.reset()
            await asyncio.sleep(0.001)
            delayTime -= self._tickTimer.stop()

        self._tickTimer.reset()
        await self._tick(delta + waitTimeSec)
        self._perfData.logicTickTime = self._tickTimer.stop() * 1000

        self._tickTimer.reset()
        await self.__renderPipe.present(delta, self._renderingTask)
        self._perfData.drawTime = self._tickTimer.stop() * 1000

        # draw perf stat
        self.__renderPipe.submitPerfData(self._perfData)


    async def __LoopWrapper(self):
        while self._bExit is False:
            await self.__Loop()
    
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
            




