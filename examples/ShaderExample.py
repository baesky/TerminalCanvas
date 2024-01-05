import baeshade as bs
import math

ray = bs.BaeRay
vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
GRAY = bs.baeColorPallette.getGrayScale
RGB = bs.baeColorPallette.RGB

# set a buffer
bs.setBuffer(42, 14)
bgcolor = GRAY(0) #GRAY(3)

def spSdf(v):
    # define a sphere in 3d location, z-front
    s = vec3(0,1,6)
    dist = (v - s).Length - 1.0
    return dist

def sdfScene(ray,start,end,steps=100):
    depth = start
    for i in range(steps):

        p = ray.Step(depth)

        dist = spSdf(p.X, p.Y, p.Z)
        if dist < 0.0001:
            dx = spSdf(vec3(p.X + 0.0001,p.Y,p.Z)) - spSdf( vec3(p.X - 0.0001,p.Y,p.Z))
            dy = spSdf(vec3(p.X,p.Y+0.0001,p.Z)) - spSdf(vec3(p.X,p.Y-0.0001,p.Z))
            dz = spSdf(vec3(p.X,p.Y,p.Z + 0.0001)) - spSdf(vec3(p.X,p.Y,p.Z-0.0001))
            mag = math.sqrt(dx*dx+dy*dy+dz*dz)
            return depth, vec3(dx/mag, dy/mag, dz/mag).Normalize(), p
        depth = depth + dist
        if depth > end:
            return end, vec3(), p

    return end, vec3(), vec3()

# per pixel
def ps(x,y, b):

    uv = (vec2(x,y) / (b.Size))
    uv -= 0.5
    #AR = b.width / b.height
    #uv.SetX(uv.X * AR )

    d = vec2.Dot(uv,uv)

    if d < 0.25:
        d = 1.0
    else:
        d = 0.0
   
    output = RGB(52 * d,0,0)

    return output

def ps2(x,y,b):
    uv = (vec2(x,y) / (b.Size))
    uv -= 0.5

    eye = vec3(0,1,0)
    dir = vec3(uv.x,uv.y,1)
    dir.Normalize()

    d,n,p = sdfScene(ray(eye,dir), 0.1, 100)

    if n.IsNearZero == True:
        return bgcolor
    

    return RGB(52 )


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