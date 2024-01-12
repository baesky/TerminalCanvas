""" Example how to draw a bitmap """

import baeshade as bs
from PIL import Image
import os
import time

vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
bgcolor = vec3(64,64,64)
util = bs.BaeshadeUtil
sprite = bs.BaeSprite
colrMode = bs.BaeColorMode

LimitFPS = 10
DisplayRate = 1.0 / LimitFPS

#read a pic
path = os.path.join(os.getcwd(),"resource/sprite.png")
pic = Image.open(path)
bmp = pic.convert('RGB')

goblin = sprite(64,64,7,10,colrMode.Color24Bits)

#extract sprite
for x in range(7):
    ptX = x * 192
    ptY = 0
    p = bmp.crop((ptX, ptY, ptX + 192, ptY + 192)).resize((64,64))
    buf = bs.BaeBuffer(p.width,p.height, mode=colrMode.Color24Bits)
    for row in range(p.height):
        for col in range(p.width):
            r,g,b = p.getpixel((col,row))
            goblin.rawFillPixel(col,row,vec3(r,g,b),x)


# config pipeline
drawPipe = bs.BaeTermDrawPipeline()
drawPipe.addPrimtive(goblin)

myTimer = util.Stopwatch()

try:
    drawPipe.useExclusiveScreen(True)
    while True:

        delta = myTimer.last()

        waitTimeSec = max(0.0,DisplayRate - delta)
        delayTime = waitTimeSec
        if delayTime > 0.005:
            time.sleep(delayTime - 0.002)
        
        while delayTime > 0:
            time.sleep(0)
            delayTime -= myTimer.last()

        drawPipe.present(delta + waitTimeSec)
        
        
        print('fixed fps:%d, perf:%.3f ms' % (LimitFPS,drawPipe.pipelinePerf*1000),end="")
except KeyboardInterrupt:
    drawPipe.useExclusiveScreen(False)


