
from enum import Enum

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

    