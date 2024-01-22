""" Example how to draw a bitmap """

import baeshade as bs
from PIL import Image
import os
import time
import math

bapp = bs.BaeApp
bkey = bs.BaeKeyboard

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
for frame in range(7):
    ptX = frame * 192
    ptY = 0
    p = bmp.crop((ptX, ptY, ptX + 192, ptY + 192)).resize((64,64))

    for row in range(p.height):
        for col in range(p.width):
            r,g,b = p.getpixel((col,row))
            goblin.rawFillPixel(col,row,vec3(r,g,b),frame)

# Create a RT to draw
RT = bs.BaeBuffer(128,64,colrMode.Color24Bits)

# config pipeline
drawPipe = bs.BaeTermDrawPipeline(RT)
drawPipe.addPrimtive(goblin)
acc = 0
def tick(delta:float):
    util.clearScreen()
    global acc
    acc = acc + delta
    v = (math.sin(acc)+1.0)*0.5
    v *= 0.5
    goblin.setPos(100*v,0)
    drawPipe.present(delta)

myApp = bapp(render=drawPipe,tick=tick)

myApp.run()