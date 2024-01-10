
from enum import Enum
import time

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
    def showCursor(bShow:bool):
        print(BaeshadeUtil.EncodeTable.ShowCursor if bShow else BaeshadeUtil.EncodeTable.HideCursor ,end="")

    @staticmethod
    def resetCursorPos(x:int = 1,y:int = 1):
        print(BaeshadeUtil.EncodeTable.CursorHomePos % (x,y), end="")

    @staticmethod
    def clearScreen():
        print(BaeshadeUtil.EncodeTable.Erase % (2), end="")


    class Stopwatch():
        """
        a simple time measure util, in seconds
        """
        
        def __init__(self):
            self._prevTime = time.perf_counter()

        def last(self):
            """
            use this for fps calculate
            """
            nowTime = time.perf_counter()
            lastTime = nowTime - self._prevTime
            self._prevTime = nowTime
            return lastTime

        def stop(self) -> float:
            """
            return time elapse from prev timing
            """
            return time.perf_counter() - self._prevTime

    