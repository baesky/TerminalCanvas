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

        for row in range(h):
            for col in range(w):
                r,g,b = p.getpixel((col%p.width,row%p.height))
                actor.rawFillPixel(col,row,vec3(r,g,b),frame)

    return actor

async def gameTick(delta:float):
    acc = time.time()
    v = (math.sin(acc)+1.0)*0.5
    v *= 0.5
    goblin.setPos(100*v,0)
    goblin2.setPos(80*v, 3)

class MyDrawSceneTask(bs.BaeRenderingTask):

    def onInit(self):
        drawer = self.DPI
        drawer.addPrimtive(ground)
        drawer.addPrimtive(goblin)
        drawer.addPrimtive(goblin2)

    def onDraw(self, delta:float):
        self.DPI.BatchDrawPrimitives(delta)

if __name__ == '__main__':

    #read a pic
    actor_path = os.path.join(os.getcwd(),"resource/sprite.png")
    bg_path = os.path.join(os.getcwd(),"resource/Tilemap_Flat.png")

    goblin = extractResource(actor_path, 64,64,7,10, colrMode.Color24Bits)
    goblin2 = extractResource(actor_path, 64,64,7,10, colrMode.Color24Bits)
    ground = extractResource(bg_path,192,64,1,0,colrMode.Color24Bits)

    # Create a RT to draw
    RTDesc = {'width':192,'height':64,'colorMode':colrMode.Color24Bits}

    myApp = bapp(RTDesc,tick_func=gameTick)

    myApp.addTask(MyDrawSceneTask())

    myApp.run()
