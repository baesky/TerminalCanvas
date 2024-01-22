""" Example how to draw a bitmap """

import baeshade as bs
from PIL import Image
import os

vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
bgcolor = vec3(64.0,64.0,64.0)
colrMode = bs.BaeColorMode
sprite = bs.BaeSprite

#read a pic
path = os.path.join(os.getcwd(),"resource/sprite.png")
pic = Image.open(path)

n = 5

s = pic.crop((n*192, 0, 192*(n+1), 192)).resize((64,64))

bmp = s.convert('RGB')

goblin = sprite(64,64,1,0,colrMode.Color24Bits)

# Create a RT to draw
RT = bs.BaeBuffer(64,64,colrMode.Color24Bits)
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

# run one frame
drawPipe.present()

print('area: %f'% (goblin._bb.area / (64*64)))

