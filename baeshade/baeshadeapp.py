from .baeshade import BaeTermDrawPipeline
from .baeshadeutil import BaeshadeUtil
import time
from typing import Optional, Callable
import signal

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

    def __tick(self,delta:float):
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

    def run(self):
        
        self.__prepareRunApp()

        try:
            while self._bExit is False:

                delta = self._frameTimer.last()
                waitTimeSec = max(0.0,self._displayRate - delta)
                delayTime = waitTimeSec
                if delayTime > 0.005:
                    time.sleep(delayTime - 0.002)
                
                while delayTime > 0:
                    time.sleep(0)
                    delayTime -= self._frameTimer.last()

                tickPerf = self._tickTimer.reset()
                self._tick(delta + waitTimeSec)
                self._tickPerf = self._tickTimer.stop()

                print('\nfixed fps:%d, tick:%.3f ms, perfX:%.3f ms, Characters Num:%d       ' % (self.LimitFPS ,self._tickPerf*1000, self._renderPipe.perfX*1000, self._renderPipe.strPerf),end="")

            #exit
            self.__exitApp()

        except KeyboardInterrupt:
            self.__exitApp()




