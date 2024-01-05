import baeshade as bs
import math

ray = bs.BaeRay
vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
GRAY = bs.baeColorPallette.getGrayScale
RGB = bs.baeColorPallette.RGB

# set a buffer
bs.setBuffer(42, 14)
bgcolor = vec3(0,0,0)

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

    uv = (vec2(x,y) / (b.Size))
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

    NDL = max(0, min(1,vec3.Dot(n,L)))

    output = c
    if NDL > 0 :
        output = c * (ltCol *  NDL) + c

    return output


# run one frame
bs.presentation(bgcolor, shader=ps)




#for i in range(int(15)):
#    print('\x1b[48;5;%dm' % (i) + "a" * int(46) + '\x1b[0m' )


#delta = 0
#idx = 0
#while True:
#    first_time = datetime.datetime.now()
#    c = idx % 7
#    for i in range(int(height)):
#        print('\x1b[6;30;%dm' % (c + 40) + " " * int(width) + '\x1b[0m' )
#    later_time = datetime.datetime.now()
#    delta = (later_time - first_time).total_seconds() * 1000
    #print(delta)
#    if(delta <1.0):
#        sleep(1.0 - delta)
#        delta = 0    
#    idx = idx + 1

#print("\x1b[48;5;$120m   aaaa\x1b[0m") 

#print('\x1b[6;30;42m' + '            ' + '\x1b[0m')