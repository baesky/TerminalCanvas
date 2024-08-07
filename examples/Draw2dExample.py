"""Example How to draw on terminal"""

from baeshade import BaeApp, BaeColorMode, BaeVec2d, BaeVec3d, BaeSprite, BaeRenderingTask, BaeshadeUtil


vec2 = BaeVec2d
vec3 = BaeVec3d
sprite = BaeSprite
bgcolor = vec3(128,128,128)

class MyDrawSceneTask(BaeRenderingTask):

    def onDraw(self, delta:float):
        dpi = self.DPI
        dpi.clearScene(bgcolor)
        #draw body
        dpi.drawSolidCircle2D(vec2(20,14), 10, vec3(170,150,64))
        dpi.drawSolidCircle2D(vec2(20,14), 9, vec3(255,255,0))
        #draw eyes
        dpi.drawLine2D(vec2(16,10),vec2(16,12), vec3(255,255,255))
        dpi.drawLine2D(vec2(17,10),vec2(17,12), vec3(0,0,0))
        dpi.drawLine2D(vec2(23,10),vec2(23,12), vec3(255,255,255))
        dpi.drawLine2D(vec2(24,10),vec2(24,12), vec3(0,0,0))
        #draw mouth
        dpi.drawLine2D(vec2(20,13),vec2(23,13), vec3(200,80,32))
        dpi.drawLine2D(vec2(20,14),vec2(22,14), vec3(200,80,32))

if __name__ == '__main__':

    # set a buffer
    RT = {'width':42,'height':28,'colorMode':BaeColorMode.Color24Bits}

    myApp = BaeApp(RT)
    myApp.addTask(MyDrawSceneTask())
    myApp.run()
    
    print(BaeshadeUtil.getTermSize())
    BaeshadeUtil.resetAttribute()