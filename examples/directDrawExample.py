from baeshade import BaeTermDrawUtils as btdu
from baeshade import ColorPallette4bit

btdu.drawText(1,1, "hello world!", ColorPallette4bit.blue, ColorPallette4bit.blue_bg_bright)
btdu.clearAfter()
btdu.drawText(1,2, "hello world!", ColorPallette4bit.blue, ColorPallette4bit.blue_bg_bright)
btdu.clearLine()
btdu.drawText(1,3, "hello world!", ColorPallette4bit.blue, ColorPallette4bit.blue_bg_bright)
btdu.clearBefore()