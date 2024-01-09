""" Example how to draw a bitmap """

import baeshade as bs
from PIL import Image
import os
import time

vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
bgcolor = vec3(64,64,64)

#read a pic
path = os.path.join(os.getcwd(),"resource/sprite.png")
pic = Image.open(path)
bmp = pic.convert('RGB')
seq = []

#extract sprite
for x in range(7):
    ptX = x * 192
    ptY = 0
    p = bmp.crop((ptX, ptY, ptX + 192, ptY + 192)).resize((64,64))
    buf = bs.BaeBuffer(p.width,round(p.height/2), mode=bs.BaeColorMode.Color24Bits)
    for row in range(p.height):
        for col in range(p.width):
            r,g,b = p.getpixel((col,row))
            buf.fillAt(col, row, vec3(r,g,b))
    seq.append(buf)

# config pipeline
drawPipe = bs.BaeTermDrawPipeline(buf=seq[0])

idx = 0
prev_time = time.perf_counter()
while True:
    print('\x1b[2J\x1b[H]',end="")
    drawPipe.bindRenderTaret(seq[idx % seq.__len__()])
    drawPipe.present()
    idx += 1
    now_time = time.perf_counter()
    delta = now_time - prev_time
    if  delta < 0.25:
        time.sleep(0.25 - delta)
        prev_time = time.perf_counter()


