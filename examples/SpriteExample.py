""" Example how to draw a bitmap """

from baeshade import BaeApp, BaeColorMode, BaeVec2d, BaeVec3d, BaeSprite, BaeRenderingTask, BaeshadeUtil
from PIL import Image
import os
import time
import math

vec3 = BaeVec3d
vec2 = BaeVec2d


LimitFPS = 10
DisplayRate = 1.0 / LimitFPS

def extractResource(path,w,h,seqNum,fps,colorMode)->BaeSprite:
    pic = Image.open(path)
    bmp = pic.convert('RGB')
    actor = BaeSprite(w,h,seqNum,fps,colorMode)
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

class MyDrawSceneTask(BaeRenderingTask):

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

    goblin = extractResource(actor_path, 64,64,7,10, BaeColorMode.Color24Bits)
    goblin2 = extractResource(actor_path, 64,64,7,10, BaeColorMode.Color24Bits)
    ground = extractResource(bg_path,192,64,1,0,BaeColorMode.Color24Bits)

    # Create a RT to draw
    RTDesc = {'width':192,'height':64,'colorMode':BaeColorMode.Color24Bits}

    myApp = BaeApp(RTDesc,tick_func=gameTick)

    myApp.addTask(MyDrawSceneTask())

    myApp.run()
