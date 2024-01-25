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

util = bs.BaeshadeUtil
sprite = bs.BaeSprite
colrMode = bs.BaeColorMode

LimitFPS = 10
DisplayRate = 1.0 / LimitFPS

def extractResource(path,w,h,seqNum,fps,colorMode)->sprite:
    pic = Image.open(path)
    bmp = pic.convert('RGB')
    actor = sprite(w,h,seqNum,fps,colorMode)
    for frame in range(seqNum):
        ptX = frame * 192
        ptY = 0
        p = bmp.crop((ptX, ptY, ptX + 192, ptY + 192)).resize((64,64))

        for row in range(p.height):
            for col in range(p.width):
                r,g,b = p.getpixel((col,row))
                actor.rawFillPixel(col,row,vec3(r,g,b),frame)

    return actor

#read a pic
actor_path = os.path.join(os.getcwd(),"resource/sprite.png")
bg_path = os.path.join(os.getcwd(),"resource/Tilemap_Flat.png")

goblin = extractResource(actor_path, 64,64,7,10, colrMode.Color24Bits)

ground = extractResource(bg_path,64,64,1,0,colrMode.Color24Bits)

# Create a RT to draw
RT = bs.BaeBuffer(128,64,colrMode.Color24Bits)

# config pipeline
drawPipe = bs.BaeTermDrawPipeline(RT)
drawPipe.addPrimtive(ground)
drawPipe.addPrimtive(goblin)
acc = 0

async def tick(delta:float):
    util.clearScreen()
    global acc
    acc = acc + delta
    v = (math.sin(acc)+1.0)*0.5
    v *= 0.5
    goblin.setPos(100*v,0)
    drawPipe.present(delta)

myApp = bapp(render=drawPipe,tick=tick)

myApp.run()