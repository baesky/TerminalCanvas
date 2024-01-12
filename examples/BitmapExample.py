""" Example how to draw a bitmap """

import baeshade as bs
from PIL import Image
import os

vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
bgcolor = vec3(64,64,64)

#read a pic
path = os.path.join(os.getcwd(),"resource/sprite.png")
pic = Image.open(path)

s = pic.crop((0, 0, 192, 192)).resize((64,64))

bmp = s.convert('RGB')

# set a buffer
buf = bs.BaeBuffer(bmp.width,round(bmp.height / 2), mode=bs.BaeColorMode.Color24Bits)

# config pipeline
drawPipe = bs.BaeTermDrawPipeline(buf=buf)

#clear canvas
drawPipe.clearScene(bgcolor)

#draw pixels
for y in range(bmp.height):
    for x in range(bmp.width):
        r,g,b = bmp.getpixel((x,y))
        # alpha pixel will trans to black during image convert to rgb, how to identify origin black?
        if r == 0 and g == 0 and b == 0:
            continue
        drawPipe.drawPixel(x,y, vec3(r,g,b))

# run one frame
drawPipe.present()


