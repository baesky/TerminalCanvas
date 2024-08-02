
from enum import Enum
import time
import sys
import shutil

class BaeshadeUtil:
    """
    utils for basic term control and misc functions
    """
    class EncodeTable(str,Enum):
        Empty = ''
        NewLine = '\n'
        CursorPos = '\x1b[%d;%dH'
        HideCursor = '\x1b[?25l'
        ShowCursor = '\x1b[?25h'
        Erase = '\x1b[%dJ'
        EnterAltBuffer = '\x1b[?1049h'
        LeaveAltBuffer = '\x1b[?1049l'
        Reset = '\x1b[0m'
        Bell = '\007'

        def __str__(self) -> str:
            return self.value
    
    @staticmethod
    def getTermSize()->tuple[int,int]:
        columns, rows = shutil.get_terminal_size()
        return columns, rows

    @staticmethod
    def output(str):
        #sys.stdout.buffer.write(str.encode('UTF-8'))
        sys.stdout.write(str)

    @staticmethod
    def flush():
        sys.stdout.flush()

    @staticmethod
    def ExclusiveScreen(bExclusive:bool):
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.EnterAltBuffer if bExclusive else BaeshadeUtil.EncodeTable.LeaveAltBuffer)

    @staticmethod
    def showCursor(bShow:bool):
        #print(BaeshadeUtil.EncodeTable.ShowCursor if bShow else BaeshadeUtil.EncodeTable.HideCursor ,end="")
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.ShowCursor if bShow else BaeshadeUtil.EncodeTable.HideCursor)

    @staticmethod
    def resetCursorPos(x:int = 1,y:int = 1):
        #print(BaeshadeUtil.EncodeTable.CursorHomePos % (x,y), end="")
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.CursorPos % (x,y))

    @staticmethod
    def clearScreen():
        #print(BaeshadeUtil.EncodeTable.Erase % (2), end="")
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.Erase % (2))

    @staticmethod
    def resetAttribute():
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.Reset)

    @staticmethod
    def restoreScreen():
        BaeshadeUtil.resetAttribute()
        BaeshadeUtil.clearScreen()
        
    @staticmethod
    def bell():
        BaeshadeUtil.output(BaeshadeUtil.EncodeTable.Bell)

    @staticmethod
    def quit():
        BaeshadeUtil.restoreScreen()
        BaeshadeUtil.showCursor(True)
        BaeshadeUtil.resetCursorPos()

    class Stopwatch():
        """
        a simple time measure util, in second
        """
        
        def __init__(self):
           self.reset()

        def last(self)->float:
            """
            use this for fps calculate
            """
            nowTime = time.perf_counter_ns()
            deltaTime = nowTime - self._prevTime
            self._prevTime = nowTime
            return deltaTime * 1e-9

        def reset(self):
             self._prevTime = time.perf_counter_ns()

        def stop(self) -> float:
            """
            return time elapse from prev timing
            """
            return (time.perf_counter_ns() - self._prevTime) * 1e-9

    