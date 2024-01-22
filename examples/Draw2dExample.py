"""Example How to draw on terminal"""

import baeshade as bs

vec2 = bs.BaeVec2d
vec3 = bs.BaeVec3d
sprite = bs.BaeSprite
bgcolor = vec3(128,128,128)
# set a buffer
buf = bs.BaeBuffer(42,28, mode=bs.BaeColorMode.Color24Bits)
# config pipeline
drawPipe = bs.BaeTermDrawPipeline(buf=buf,debug=False)

#clear canvas
drawPipe.clearScene(bgcolor)

#draw body
drawPipe.drawSolidCircle2D(vec2(20,14), 10, vec3(170,150,64))
drawPipe.drawSolidCircle2D(vec2(20,14), 9, vec3(255,255,0))
#draw eyes
drawPipe.drawLine2D(vec2(16,10),vec2(16,12), vec3(255,255,255))
drawPipe.drawLine2D(vec2(17,10),vec2(17,12), vec3(0,0,0))
drawPipe.drawLine2D(vec2(23,10),vec2(23,12), vec3(255,255,255))
drawPipe.drawLine2D(vec2(24,10),vec2(24,12), vec3(0,0,0))
#draw mouth
drawPipe.drawLine2D(vec2(20,13),vec2(23,13), vec3(200,80,32))
drawPipe.drawLine2D(vec2(20,14),vec2(22,14), vec3(200,80,32))
# run one frame
drawPipe.encodeRT()