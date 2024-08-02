import math

"""
simple math utilities, performance is not guaranteed.
"""

class BaeVec2d:
    __slots__ = ['X', 'Y', '_eps']
    def __init__(self, x=0,y=0,eps=0.000001):
        self.X = x
        self.Y = y
        self._eps = eps

    def __add__(self, o):
        return BaeVec2d(self.X + o.X, self.Y + o.Y)
    
    def __iadd__(self, o):
        if isinstance(o, float):
            return BaeVec2d(self.X + o, self.Y + o)
        else:
            return BaeVec2d(self.X + o.X, self.Y + o.Y)

    def __sub__(self,o):
        if isinstance(o, BaeVec2d):
            return BaeVec2d(self.X - o.X, self.Y - o.Y)
        else:
            return BaeVec2d(self.X - o, self.Y - o)

    def __isub__(self,o):
        if isinstance(o, float):
            return BaeVec2d(self.X - o, self.Y - o)
        else:
            return BaeVec2d(self.X - o.X, self.Y - o.Y)

    def __mul__(self, f):
        return BaeVec2d(self.X * f, self.Y * f)
    
    def __truediv__(self, f):
        if isinstance(f, float):
            return BaeVec2d(self.X / f, self.Y /f)
        elif isinstance(f, int):
            return BaeVec2d(self.X / f, self.Y /f)
        else:
            return BaeVec2d(self.X / f.X, self.Y /f.Y)

    def __eq__(self, o):
        return abs(self.X - o.X) < self._esp and abs(self.Y - o.Y) < self._esp
    
    def __ne__(self, o):
        return not(self == o)
    
    @property
    def Length(self):
        return math.sqrt(self.X*self.X+self.Y*self.Y)

    @staticmethod
    def Dot(lh , rh):
        return lh.X * rh.X + lh.Y * rh.Y

class BaeVec3d(BaeVec2d):
    __slots__ = ['Z']  
    def __init__(self, x=0,y=0,z=0,esp=0.000001):
        super().__init__(x,y,esp)
        self.Z = z

    @property
    def Length(self):
        return math.sqrt(self.X*self.X+self.Y*self.Y+self.Z*self.Z)
    
    def Normalize(self):
        len = self.Length
        self.X = self.X / len
        self.Y = self.Y / len
        self.Z = self.Z / len
        return self

    def __add__(self,o):
        if isinstance(o, BaeVec3d):
            return BaeVec3d(self.X + o.X, self.Y + o.Y, self.Z + o.Z)
        else:
            return BaeVec3d(self.X + o, self.Y + o, self.Z + o)

    def __iadd__(self,o):
        if isinstance(o, float):
            return BaeVec3d(self.X + o, self.Y + o, self.Z + o)
        else:
            return BaeVec3d(self.X + o.X, self.Y + o.Y, self.Z + o.Z)

    def __sub__(self,o):
        if isinstance(o, BaeVec3d):
            return BaeVec3d(self.X - o.X, self.Y - o.Y, self.Z - o.Z)
        else:
            return BaeVec3d(self.X - o, self.Y - o, self.Z - o)
    
    def __isub__(self,o):
        if isinstance(o, float):
            return BaeVec3d(self.X - o, self.Y - o, self.Z - o)
        else:
            return BaeVec3d(self.X - o.X, self.Y - o.Y, self.Z - o.Z)

    def __mul__(self, f):
        if isinstance(f, BaeVec3d):
            return BaeVec3d(self.X * f.X, self.Y * f.Y, self.Z * f.Z )
        else:
            return BaeVec3d(self.X * f, self.Y * f, self.Z * f )
        
    def __rmul__(self, f):
        return self.__mul__(f)
    
    def __truediv__(self, f):
        if isinstance(f, float):
            return BaeVec3d(self.X / f, self.Y /f, self.Z / f)
        elif isinstance(f, int):
            return BaeVec3d(self.X / f, self.Y /f, self.Z / f)
        else:
            return BaeVec3d(self.X / f.X, self.Y /f.Y, self.Z / f.Z)

    def __eq__(self, o):
        return abs(self.X - o.X) < self._eps and \
                abs(self.Y - o.Y) < self._eps and \
                abs(self.Z - o.Z) < self._eps
    
    def __ne__(self, o):
        return not(self == o)

    @staticmethod
    def Dot(lh , rh):
        return lh.X * rh.X + lh.Y * rh.Y + lh.Z * rh.Z

    @property
    def IsNearZero(self):
        return self.Length < 0.000001    

class BaeRay:
    def __init__(self, v, d):
        self._o = v
        self._dir = d

    def Step(self,t):
        p = self._o + self._dir * t
        return BaeVec3d(p.X,p.Y,p.Z)
    
class BaeMathUtil:

    __p = float(10**5)

    @staticmethod
    def clamp(v,b,t):
        """
        clamp value v at: b <= v <= t
        """
        return max(b, min(v,t))
    
    @staticmethod
    def round(v:float)->int:
        return int(v)
    
    @staticmethod
    def lerp(a,b,t):
        return a + (b - a) * t
    
    def cos(v):
        if isinstance(v, BaeVec3d):
            return BaeVec3d(math.cos(v.X), math.cos(v.Y), math.cos(v.Z))
        elif isinstance(v, BaeVec2d):
            return BaeVec2d(math.cos(v.X), math.cos(v.Y))
        else:
            return math.cos(v)

class BaeBoundingBox2D:
    def __init__(self):
        self._min = BaeVec2d(9999,9999)
        self._max = BaeVec2d(-9999,-9999)

    def addPoint(self,x,y):
        
        if x < self._min.X:
            self._min.X = x
        elif x > self._max.X:
            self._max.X = x

        if y < self._min.Y:
            self._min.Y = y
        elif y > self._max.Y:
            self._max.X = y

    @property
    def area(self):
        return (self._max.X - self._min.X) * (self._max.Y - self._min.Y)

    