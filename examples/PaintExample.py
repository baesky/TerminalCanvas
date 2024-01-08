"""Example How to draw on terminal"""

import baeshade as bs

vec2 = bs.BaeVec2d
vec3 = bs.BaeVec3d
bgcolor = vec3(0,0,0)
# set a buffer
buf = bs.BaeBuffer(42,14, mode=bs.BaeColorMode.Color24Bits)
# config pipeline
drawPipe = bs.BaeTermDrawPipeline(buf=buf,debug=False)

#clear canvas
drawPipe.clearScene(bgcolor)

#draw something
drawPipe.drawLine(vec2(0,0),vec2(13,13), vec3(123,0,0))

# run one frame
drawPipe.present()