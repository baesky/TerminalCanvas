
from enum import Enum
import time
import sys

class BaeshadeUtil:
    class EncodeTable(str,Enum):
        Empty = ''
        NewLine = '\n'
        CursorHomePos = '\x1b[%d;%dH'
        HideCursor = '\x1b[?25l'
        ShowCursor = '\x1b[?25h'
        Erase = '\x1b[%dJ'

        def __str__(self) -> str:
            return self.value
    
    @staticmethod
    def output(str):
        sys.stdout.write(str)

    @staticmethod
    def showCursor(bShow:bool):
        #print(BaeshadeUtil.EncodeTable.ShowCursor if bShow else BaeshadeUtil.EncodeTable.HideCursor ,end="")
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.ShowCursor if bShow else BaeshadeUtil.EncodeTable.HideCursor)

    @staticmethod
    def resetCursorPos(x:int = 1,y:int = 1):
        #print(BaeshadeUtil.EncodeTable.CursorHomePos % (x,y), end="")
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.CursorHomePos % (x,y))

    @staticmethod
    def clearScreen():
        #print(BaeshadeUtil.EncodeTable.Erase % (2), end="")
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.Erase % (2))


    @staticmethod
    def quit():
        BaeshadeUtil.clearScreen()
        BaeshadeUtil.showCursor(True)
        BaeshadeUtil.resetCursorPos()

    class Stopwatch():
        """
        a simple time measure util, in milliseconds
        """
        
        def __init__(self):
            self._prevTime = time.perf_counter_ns()

        def last(self)->float:
            """
            use this for fps calculate
            """
            nowTime = time.perf_counter_ns()
            lastTime = nowTime - self._prevTime
            self._prevTime = nowTime
            return lastTime * 1e-6

        def stop(self) -> float:
            """
            return time elapse from prev timing
            """
            return (time.perf_counter_ns() - self._prevTime) * 1e-6

    