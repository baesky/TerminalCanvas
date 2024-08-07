"""Example How to draw use a shader"""

from baeshade import BaeApp, BaeColorMode, BaeRenderingTask, BaeRay, BaeVec3d, BaeVec2d
import math

Ray = BaeRay
vec3 = BaeVec3d
vec2 = BaeVec2d
bgcolor = vec3(0,0,0)

def spSdf(v):
    # define a sphere in 3d location, z-front
    s = vec3(0,1,4)
    d = v - s
    dist = d.Length - 1.0

    return dist, vec3(128,0,0)

def spFloor(v):
    return v.Y, vec3(128,128,128)

def sdfScene(ray,start,end,steps=100):
    depth = start
    for i in range(steps):

        p = ray.Step(depth)

        # 0: sphere, 1: plane
        t = 0
        dist, c = spSdf(p)
        dist2, c2 = spFloor(p)
        if dist > dist2:
            dist = dist2
            c = c2
            t = 1

        if t == 0:
            if dist < 0.0001:
                dx1, _ = spSdf(vec3(p.X + 0.0001,p.Y,p.Z))
                dx2, _ = spSdf( vec3(p.X - 0.0001,p.Y,p.Z))
                dy1, _ = spSdf(vec3(p.X,p.Y+0.0001,p.Z))
                dy2, _ = spSdf(vec3(p.X,p.Y-0.0001,p.Z))
                dz1, _ = spSdf(vec3(p.X,p.Y,p.Z + 0.0001))
                dz2, _ = spSdf(vec3(p.X,p.Y,p.Z-0.0001))
                dx = dx1 - dx2
                dy = dy1 - dy2
                dz = dz1 - dz2
                mag = math.sqrt(dx*dx+dy*dy+dz*dz)
                return depth, vec3(dx/mag, dy/mag, dz/mag).Normalize(), p, c
        else:
            if dist < 0.0001:
                return depth, vec3(0,1,0), p, c

        
        depth = depth + dist
        if depth > end:
            return end, vec3(), p, bgcolor

    return end, vec3(), vec3(), bgcolor

def initRay(x,y,buffsize,eye):
    uv = vec2(x,y) / buffsize
    uv -= 0.5
    uv.Y = (uv.Y * -1.0)

    dir = vec3(uv.X,uv.Y,1).Normalize()
    return Ray(eye,dir)

def pixelShader(x,y,b):

    res = vec2(b['bw'],b['bh'])
    eye = vec3(0,1,0)
    d,n,p,c = sdfScene(initRay(x,y,res,eye), 0.1, 100)

    if n.IsNearZero == True:
        return bgcolor
    
    ltPos = vec3(-2,3.5,0)
    ltCol = vec3(1,1,1) * 2.2

    L = (ltPos - p).Normalize()

    NDL = max(0.0, min(1.0,vec3.Dot(n,L)))

    shadowRayPos = p + n*0.01
    shadowRay = Ray(shadowRayPos,L)
    d,n,p,c1 = sdfScene(shadowRay, 0.1, 30.0)
    if d < 10.0:
        c = c * d/10.0

    output = c * (ltCol *  NDL)

    return output


class ShaderExampleTask(BaeRenderingTask):
    def onDraw(self, delta: float):
        self.DPI.runShader(pixelShader)


if __name__ == '__main__':
    # set a RT desc
    RT = {'width':42,'height':28,'colorMode':BaeColorMode.Color24Bits}

    # config app
    app = BaeApp(RT)
    app.addTask(ShaderExampleTask())
    app.run()
