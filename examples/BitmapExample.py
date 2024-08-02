""" Example how to draw a bitmap """

import baeshade as bs
from baeshade import BaeApp, BaeVec3d, BaeVec2d, BaeColorMode, BaeSprite
from PIL import Image
import os

vec3 = BaeVec3d
vec2 = BaeVec2d
bgcolor = vec3(64.0,64.0,64.0)

class MyDrawSceneTask(bs.BaeRenderingTask):

    def onInit(self):
        self.DPI.addPrimtive(goblin)
    def onDraw(self, delta:float):
        self.DPI.BatchDrawPrimitives(delta)

if __name__ == '__main__':

    #read a pic
    path = os.path.join(os.getcwd(),"resource/sprite.png")
    pic = Image.open(path)

    # sprite sheet index
    n = 5

    s = pic.crop((n*192, 0, 192*(n+1), 192)).resize((64,64))

    bmp = s.convert('RGB')

    goblin = BaeSprite(64,64,1,0,BaeColorMode.Color24Bits)

    # Create a RT to draw
    RT = {'width':64,'height':64,'colorMode':BaeColorMode.Color24Bits}

    #draw pixels
    for y in range(bmp.height):
        for x in range(bmp.width):
            r,g,b = bmp.getpixel((x,y))
            # alpha pixel will trans to black during image convert to rgb, how to identify origin black?
            #if r == 0 and g == 0 and b == 0:
            #    continue
            goblin.rawFillPixel(x,y,vec3(r,g,b))

    myApp = BaeApp(RT)
    myApp.addTask(MyDrawSceneTask())
    myApp.run()


    print('area: %f'% (goblin._bb.area / (64*64)))

