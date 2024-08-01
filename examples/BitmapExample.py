""" Example how to draw a bitmap """

import baeshade as bs
from PIL import Image
import os

bapp = bs.BaeApp
vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
bgcolor = vec3(64.0,64.0,64.0)
colrMode = bs.BaeColorMode
sprite = bs.BaeSprite

class MyDrawSceneTask(bs.BaeRenderingTask):

    def onDraw(self, delta:float):
        self.getDPI().BatchDrawPrimitives(delta)

if __name__ == '__main__':

    #read a pic
    path = os.path.join(os.getcwd(),"resource/sprite.png")
    pic = Image.open(path)

    # sprite sheet index
    n = 5

    s = pic.crop((n*192, 0, 192*(n+1), 192)).resize((64,64))

    bmp = s.convert('RGB')

    goblin = sprite(64,64,1,0,colrMode.Color24Bits)

    # Create a RT to draw
    RT = {'width':64,'height':64,'colorMode':colrMode.Color24Bits}
    # config pipeline
    drawPipe = bs.BaeTermDrawPipeline(RT)

    #draw pixels
    for y in range(bmp.height):
        for x in range(bmp.width):
            r,g,b = bmp.getpixel((x,y))
            # alpha pixel will trans to black during image convert to rgb, how to identify origin black?
            #if r == 0 and g == 0 and b == 0:
            #    continue
            goblin.rawFillPixel(x,y,vec3(r,g,b))

    # add prim to draw
    drawPipe.addPrimtive(goblin)

    myApp = bapp(renderer=drawPipe)
    myApp.addTask(MyDrawSceneTask())
    myApp.run()


    print('area: %f'% (goblin._bb.area / (64*64)))

