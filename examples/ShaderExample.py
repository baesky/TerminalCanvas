import baeshade as bs
import math

ray = bs.BaeRay
vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
bgcolor = vec3(0,0,0)
baedraw = bs.BaeTermDraw

def spSdf(v):
    # define a sphere in 3d location, z-front
    s = vec3(0,1,4)
    d = v - s
    dist = d.Length - 1.0

    return dist, vec3(52,0,0)

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

def ps(x,y,b):

    uv = (vec2(x,y) / (b.size))
    uv -= 0.5
    uv.SetY(uv.Y * -1.0)

    eye = vec3(0,1,0)
    dir = vec3(uv.X,uv.Y,1).Normalize()

    d,n,p,c = sdfScene(ray(eye,dir), 0.1, 100)

    if n.IsNearZero == True:
        return bgcolor
    
    ltPos = vec3(-2,3.5,0)
    ltCol = vec3(1,1,1) * 2.2

    L = (ltPos - p).Normalize()

    NDL = max(0.0, min(1.0,vec3.Dot(n,L)))

    output = c * (ltCol *  NDL)

    return output

# set a buffer
buf = bs.BaeBuffer(42,14, mode=bs.BaeColorMode.Color24Bits)
drawPipe = bs.BaeTermDrawPipeline(buf=buf,ps=ps)

# run one frame
baedraw.present(drawPipe, clrCol=bgcolor)
