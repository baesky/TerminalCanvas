import baeshade as bs
import math

GRAY = bs.baeColorPallette.getGrayScale
RGB = bs.baeColorPallette.RGB

# set a buffer
bs.setBuffer(46, 23)
bgcolor = GRAY(3)

def spSdf(x,y,z):
    return math.sqrt(x*x+y*y+z*z) - 1.0

def rayDir(fov, bufx, bufy, tcx, tcy):
    x = tcx - bufx / 2
    y = tcy - bufy / 2
    z = bufy / math.tan(math.radians(fov)/2) * 1.0
    l = math.sqrt(x*x+y*y+z*z)
    return x/l, y/l, -z/l

def sdfScene(ex,ey,ez,rx,ry,rz,start,end):
    depth = start
    for i in range(100):
        px = ex + rx*depth
        py = ey + ry*depth
        pz = ez + rz*depth
        dist = spSdf(px, py, pz)
        if dist < 0.0001:
            dx = spSdf(px + 0.0001,py,pz) - spSdf(px - 0.0001,py,pz)
            dy = spSdf(px,py+0.0001,pz) - spSdf(px,py-0.0001,pz)
            dz = spSdf(px,py,pz + 0.0001) - spSdf(px,py,pz-0.0001)
            mag = math.sqrt(dx*dx+dy*dy+dz*dz)
            return depth, dx/mag, dy/mag, dz/mag,px,py,pz
        depth = depth + dist
        if depth > end:
            return end, 0,0,0,px,py,pz

    return end, 0,0,0, ex,ey,ez

def ps(x,y, b):

    rx,ry,rz = rayDir(45.0, b.width, b.height, x, y)
    
    dist,nx,ny,nz,hitx,hity,hitz = sdfScene(0.0, 0.0, 5.0, rx, ry, rz, 0.0, 100.0)
    eps = 100.0 - 0.0001
    if dist > eps:
        return RGB(0,0,0)

    #light pos - hit location = L
    ltx = 4.0 - hitx
    lty = 2.0 - hity
    ltz = 3.0 - hitz

    ltMag = math.sqrt(ltx*ltx+lty*lty+ltz*ltz)

    ltx = ltx / ltMag
    lty = lty / ltMag
    ltz = ltz / ltMag

    ndl = nx*ltx+ny*lty+nz*ltz
    ndl = max(0,min(1,ndl))
    output = RGB(52,0,0)
    if ndl > 0:
        output = RGB( 52 + int(200*ndl),0,0)
    return output

bs.presentation(bgcolor, shader=ps, ar=1.3)




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