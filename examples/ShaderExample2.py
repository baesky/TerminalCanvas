import numpy as np
import math

# reference: https://www.shadertoy.com/view/MdXyzX

# Constants from the shader
DRAG_MULT = 0.38
WATER_DEPTH = 1.0
CAMERA_HEIGHT = 1.5
ITERATIONS_RAYMARCH = 12
ITERATIONS_NORMAL = 37

# Normalize mouse coordinates function (dummy implementation)
def NormalizedMouse(iMouse, iResolution):
    return iMouse[0] / iResolution[0], iMouse[1] / iResolution[1]

# wavedx function implementation
def wavedx(position, direction, frequency, timeshift):
    x = np.dot(direction, position) * frequency + timeshift
    wave = math.exp(math.sin(x) - 1.0)
    dx = wave * math.cos(x)
    return wave, -dx

# getwaves function implementation
def getwaves(position, iterations):
    wavePhaseShift = np.linalg.norm(position) * 0.1
    iter_val = 0.0
    frequency = 1.0
    timeMultiplier = 2.0
    weight = 1.0
    sumOfValues = 0.0
    sumOfWeights = 0.0
    for i in range(iterations):
        p = np.array([math.sin(iter_val), math.cos(iter_val)])
        res_wave, res_dx = wavedx(position, p, frequency, timeMultiplier + wavePhaseShift)

        position += p * res_dx * weight * DRAG_MULT
        sumOfValues += res_wave * weight
        sumOfWeights += weight

        weight = np.interp(weight, [weight, 0.0], [1.0, 0.2])
        frequency *= 1.18
        timeMultiplier *= 1.07

        iter_val += 1232.399963

    return sumOfValues / sumOfWeights

# normal function implementation
def normal(pos, e, depth):
    ex = np.array([e, 0.0])
    H = getwaves(pos, ITERATIONS_NORMAL) * depth
    a = np.array([pos[0], H, pos[1]])
    b1 = np.array([pos[0] - e, getwaves(pos - ex, ITERATIONS_NORMAL) * depth, pos[1]])
    b2 = np.array([pos[0], getwaves(pos + ex[::-1], ITERATIONS_NORMAL) * depth, pos[1] + e])
    N = np.cross(a - b1, a - b2)
    return N / np.linalg.norm(N)

# Raymarches the ray from top water layer boundary to low water layer boundary
def raymarchwater(camera, start, end, depth):
    pos = start
    dir = (end - start) / np.linalg.norm(end - start)
    
    for i in range(64):
        # Calculate height based on wave simulation
        height = getwaves(pos[:2], ITERATIONS_RAYMARCH) * depth - depth
        
        # Check if ray intersects with water surface
        if height + 0.01 > pos[1]:
            return np.linalg.norm(pos - camera)
        
        # Move forward according to the height mismatch
        pos += dir * (pos[1] - height)
    
    # Assume hit the top layer if no intersection found (for performance)
    return np.linalg.norm(start - camera)

# getRay function (simplified)
def getRay(fragCoord, iResolution):
    uv = ((fragCoord / iResolution) * 2.0 - 1.0) * np.array([iResolution[0] / iResolution[1], 1.0])
    proj = np.array([uv[0], uv[1], 1.5])
    return proj

# Main function for raymarching and visualization
def mainImage(fragCoord, iResolution, iTime, iMouse):
    # Get the ray direction
    ray = getRay(fragCoord, iResolution)
    if ray[1] >= 0.0:
        # Render sky if ray direction is positive
        return np.array([0.0, 0.0, 0.0])  # Black sky
    else:
        # Render water if ray direction is negative
        origin = np.array([iTime * 0.2, CAMERA_HEIGHT, 1.0])
        waterPlaneHigh = np.array([0.0, 0.0, 0.0])
        waterPlaneLow = np.array([0.0, -WATER_DEPTH, 0.0])

        highPlaneHit = intersectPlane(origin, ray, waterPlaneHigh, np.array([0.0, 1.0, 0.0]))
        lowPlaneHit = intersectPlane(origin, ray, waterPlaneLow, np.array([0.0, 1.0, 0.0]))

        highHitPos = origin + ray * highPlaneHit
        lowHitPos = origin + ray * lowPlaneHit

        dist = raymarchwater(origin, highHitPos, lowHitPos, WATER_DEPTH)
        waterHitPos = origin + ray * dist

        N = normal(waterHitPos[:2], 0.01, WATER_DEPTH)
        N = np.interp(N, [-1.0, 1.0], [0.0, 1.0])  # Normalize N for visualization

        fresnel = (0.04 + (1.0 - 0.04) * (pow(1.0 - max(0.0, np.dot(-N, ray)), 5.0)))
        R = np.array(reflect(ray, N))
        R[1] = abs(R[1])

        reflection = getAtmosphere(R)  # Simplified
        scattering = np.array([0.0, 0.0, 0.0])  # Simplified

        C = fresnel * reflection + scattering
        return C * 2.0  # Tone mapping

# Ray-Plane intersection checker (simplified)
def intersectPlane(origin, direction, point, normal):
    return np.clip(np.dot(point - origin, normal) / np.dot(direction, normal), -1.0, 9991999.0)

# Helper function to reflect ray
def reflect(ray, N):
    return ray - 2.0 * np.dot(ray, N) * N

# Dummy implementation of atmosphere and sun functions
def getAtmosphere(dir):
    return np.array([0.3, 0.3, 0.3])  # Dummy atmosphere color

def getSun(dir):
    return 3.0  # Dummy sun color

# Dummy implementation of tonemapping function
def aces_tonemap(color):
    return np.clip(color, 0.0, 1.0)

# Example usage
iResolution = np.array([800.0, 600.0])
iTime = 1.0
iMouse = np.array([400.0, 300.0])

fragCoord = np.array([400.0, 300.0])  # Example fragment coordinate

# Output color
fragColor = mainImage(fragCoord, iResolution, iTime, iMouse)
print("Fragment color:", fragColor)
