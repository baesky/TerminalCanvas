import numpy as np
import math
import baeshade as bs
import math

butil = bs.BaeMathUtil
colrMode = bs.BaeColorMode
Ray = bs.BaeRay
vec3 = bs.BaeVec3d
vec2 = bs.BaeVec2d
# reference: https://www.shadertoy.com/view/MdXyzX

# Constants from the shader
DRAG_MULT = 0.58
WATER_DEPTH = 1.3
CAMERA_HEIGHT = 1.5
ITERATIONS_RAYMARCH = 8#12
ITERATIONS_NORMAL = 12
NormalizedMouse = np.array([0.5, 0.8])

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def reflect(vector, normal):
    # Ensure that the normal is normalized
    normal = normal / np.linalg.norm(normal)
    
    # Calculate the dot product of vector and normal
    dot_product = np.dot(vector, normal)
    
    # Compute the reflection vector
    reflection = vector - 2 * dot_product * normal
    
    return reflection

def dot(v1, v2):
    return np.dot(v1, v2)

def mix(x, y, a):
    return x * (1 - a) + y * a

def distance(v1, v2):
    return np.linalg.norm(v1 - v2)

def wavedx(position, direction, frequency, timeshift):

    x = np.dot(direction, position) * frequency + timeshift
    wave = np.exp(np.sin(x) - 1.0)
    dx = wave * np.cos(x)
    return np.array([wave, -dx])


def getwaves(position, iterations, iTime):
    wavePhaseShift = np.linalg.norm(position) * 0.1
    iter_val = 0.0 
    frequency = 1.0  
    timeMultiplier = 2.0  
    weight = 1.0 
    sumOfValues = 0.0 
    sumOfWeights = 0.0 

    for i in range(iterations):
        p = np.array([np.sin(iter_val), np.cos(iter_val)])
        res = wavedx(position, p, frequency, iTime * timeMultiplier + wavePhaseShift)

        position += p * res[1] * weight * DRAG_MULT

        sumOfValues += res[0] * weight
        sumOfWeights += weight

        weight = np.interp(0.2, [0, 1], [weight, 0.0])
        frequency *= 1.18
        timeMultiplier *= 1.07

        iter_val += 1232.399963

    return sumOfValues / sumOfWeights

def raymarchwater(camera, start, end, depth, iTime):
    pos = start.copy()
    dir = normalize(end - start)
    
    for i in range(32):
        # 高度从 0 到 -depth
        height = getwaves(pos[:2], ITERATIONS_RAYMARCH, iTime) - depth
        
        # 如果波形高度几乎匹配光线高度，则返回命中距离
        if height + 0.01 > pos[1]:
            return distance(pos, camera)
        
        # 根据高度差进行前进
        pos += dir * (pos[1] - height)
    
    # 如果没有检测到命中，则假定命中上层，返回初始位置到相机的距离
    return distance(start, camera)

def normal(pos, e, depth):
    ex = np.array([e, 0])
    
    # 计算当前位置的高度
    H = getwaves(pos, ITERATIONS_NORMAL, depth)
    a = np.array([pos[0], H, pos[1]])
    
    # 计算两个相邻位置的高度
    b = np.array([pos[0] - e, getwaves(pos - ex, ITERATIONS_NORMAL, depth), pos[1]])
    c = np.array([pos[0], getwaves(pos + ex[::-1], ITERATIONS_NORMAL, depth), pos[1] + e])
    
    # 计算叉积并归一化
    n = np.cross(a - b, a - c)
    return normalize(n)

def getRay(fragCoord, iResolution):
    uv = ((fragCoord / iResolution) * 2.0 - 1.0) * np.array([iResolution[0] / iResolution[1], 1.0])
    uv[1] = - uv[1]
    proj = normalize(np.array([uv[0], uv[1]-0.5, 1.5]))
    
    return proj


def clamp(x, min_val, max_val):
    return max(min(x, max_val), min_val)

def intersectPlane(origin, direction, point, normal):
    numerator = np.dot(point - origin, normal)
    denominator = np.dot(direction, normal)
    t = numerator / denominator
    return clamp(t, -1.0, 9991999.0)

def extra_cheap_atmosphere(raydir, sundir):
    sundir[1] = max(sundir[1], -0.07)
    special_trick = 1.0 / (raydir[1] * 1.0 + 0.1)
    special_trick2 = 1.0 / (sundir[1] * 11.0 + 1.0)
    raysundt = np.power(abs(dot(sundir, raydir)), 2.0)
    sundt = np.power(max(0.0, dot(sundir, raydir)), 8.0)
    mymie = sundt * special_trick * 0.2
    
    suncolor = mix(np.array([1.0, 1.0, 1.0]), 
                   np.maximum(np.array([0.0, 0.0, 0.0]), np.array([1.0, 1.0, 1.0]) - np.array([5.5, 13.0, 22.4]) / 22.4), 
                   special_trick2)
    
    bluesky = np.array([5.5, 13.0, 22.4]) / 22.4 * suncolor
    
    bluesky2 = np.maximum(np.array([0.0, 0.0, 0.0]), 
                          bluesky - np.array([5.5, 13.0, 22.4]) * 0.002 * (special_trick + -6.0 * sundir[1] * sundir[1]))
    
    bluesky2 *= special_trick * (0.24 + raysundt * 0.24)
    
    return bluesky2 * (1.0 + 1.0 * np.power(1.0 - raydir[1], 3.0))

def getSunDirection():
    return normalize(np.array([1.2, 1.0, 0.2]))

def getAtmosphere(dir):
    sundir = getSunDirection()
    return extra_cheap_atmosphere(dir, sundir) * 0.5

def aces_tonemap(color):
    m1 = np.array([
        [0.59719, 0.07600, 0.02840],
        [0.35458, 0.90834, 0.13383],
        [0.04823, 0.01566, 0.83777]
    ])

    m2 = np.array([
        [1.60475, -0.10208, -0.00327],
        [-0.53108, 1.10813, -0.07276],
        [-0.07367, -0.00605, 1.07602]
    ])
    

    v = np.dot(m1, color)
    a = v * (v + 0.0245786) - 0.000090537
    b = v * (0.983729 * v + 0.4329510) + 0.238081

    result = np.dot(m2, a / b)
    result = np.clip(result, 0.0, 1.0)

    return np.power(result, 1.0 / 2.2)

def pixelShaderEX(x,y, b):
    fragCoord = np.array([x,y])
    iResolution = np.array([b['bw'],b['bh']])
    iTime = b['time']
    ray = getRay(fragCoord, iResolution)

    if ray[1] >= 0.0:
        C = getAtmosphere(ray)
        fragColor = np.array(list(aces_tonemap(C * 2.0)))
    else:
        waterPlaneHigh = np.array([0.0, 0.0, 0.0])
        waterPlaneLow = np.array([0.0, -WATER_DEPTH, 0.0])
        origin = np.array([0.2, CAMERA_HEIGHT, 1.0])

        highPlaneHit = intersectPlane(origin, ray, waterPlaneHigh, np.array([0.0, 1.0, 0.0]))
        lowPlaneHit = intersectPlane(origin, ray, waterPlaneLow, np.array([0.0, 1.0, 0.0]))

        highHitPos = origin + ray * highPlaneHit
        lowHitPos = origin + ray * lowPlaneHit

        dist = raymarchwater(origin, highHitPos, lowHitPos, WATER_DEPTH, iTime)
        waterHitPos = origin + ray * dist

        N = normal(np.array([waterHitPos[0],waterHitPos[2]]), 0.01, WATER_DEPTH)
        #N = mix(N, np.array([0.0, 1.0, 0.0]), 0.8 * min(1.0, np.sqrt(dist * 0.01) * 1.1))

        fresnel = (0.04 + (1.0 - 0.04) * np.power(1.0 - max(0.0, dot(-N, ray)), 5.0))

        R = normalize(reflect(ray, N))
        R[1] = abs(R[1])

        reflection = getAtmosphere(R)
        scattering = np.array([0.0293, 0.0698, 0.1717]) * 0.1 * (0.2 + (waterHitPos[1] + WATER_DEPTH) / WATER_DEPTH)

        C = fresnel * reflection + scattering

        fragColor = aces_tonemap(C * 2.0)

    return vec3(fragColor[0]*255,fragColor[1]*255,fragColor[2]*255)

#reference:https://www.shadertoy.com/view/mtyGWy
def palette( t )->vec3:
    a = vec3(0.5, 0.5, 0.5);
    b = vec3(0.5, 0.5, 0.5);
    c = vec3(1.0, 1.0, 1.0);
    d = vec3(0.263,0.416,0.557);

    tmp1 = c*t+d
    tmp =  6.28318*(tmp1)
    return a + b*butil.cos(tmp );

def pixelShader(x,y, b):
    frageCoord = vec2(x,y)
    iResolution = vec2(b['bw'],b['bh'])
    uv = (frageCoord * 2.0 - iResolution) / iResolution.Y;
    uv0 = uv;
    finalColor = vec3(0.0);
    iTime = b['time']

    for i in range(4):
        uv = uv * 1.5 - uv - 0.5

        d = uv.Length * math.exp(-uv0.Length);

        col = palette(uv0.Length + i*.4 + iTime*.4);

        d = math.sin(d*8. + iTime)/8.;
        d = abs(d);

        d = pow(0.01 / d, 1.2);

        finalColor += col * d;
    
        
    return finalColor*255



if __name__ == '__main__':
    # set a RT desc
    RT = {'width':42,'height':28,'colorMode':colrMode.Color24Bits}
    #RT = {'width':142,'height':68,'colorMode':colrMode.Color24Bits}
    # config pipeline
    drawPipe = bs.BaeTermDrawPipeline(RT)
    drawPipe.setShader(pixelShader)

    # config app
    app = bs.BaeApp(drawPipe)
    app.run()