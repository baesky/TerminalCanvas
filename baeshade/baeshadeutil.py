
from enum import Enum

class BaeshadeUtil:
    class EncodeTable(str,Enum):
        Empty = ''
        NewLine = '\n'
        CursorHomePos = '\x1b[H'

        def __str__(self) -> str:
            return self.value
        