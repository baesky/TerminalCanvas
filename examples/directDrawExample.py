from baeshade import BaeTermDrawUtils as btdu
from baeshade import ColorPallette4bit

## example 1
## uncomment below to run the example 1
# btdu.drawText(1,1, "hello world!", ColorPallette4bit.blue, ColorPallette4bit.blue_bg_bright)
# btdu.clearAfter()
# btdu.drawText(1,2, "hello world!", ColorPallette4bit.blue, ColorPallette4bit.blue_bg_bright)
# btdu.clearLine()
# btdu.drawText(1,3, "hello world!", ColorPallette4bit.blue, ColorPallette4bit.blue_bg_bright)
# btdu.clearBefore()

## example 2
import time
for i in range(20):
    btdu.drawText(i+1, 5, "▤", ColorPallette4bit.green)
    btdu.drawText(25,5, f"progress:{(i+1)*5}%", ColorPallette4bit.cyan)
    time.sleep(0.5)