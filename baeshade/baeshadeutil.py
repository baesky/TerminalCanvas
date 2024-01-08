import math
        
class BaeVec2d:
    def __init__(self, x=0.0,y=0.0):
        self._x = x
        self._y = y

    @property
    def X(self):
        return self._x

    @property
    def Y(self):
        return self._y
    
    def SetX(self,v):
        self._x = v

    def SetY(self,v):
        self._y = v

    def __add__(self, o):
        return BaeVec2d(self.X + o.X, self.Y + o.Y)
    
    def __iadd__(self, o):
        if isinstance(o, float):
            return BaeVec2d(self.X + o, self.Y + o)
        else:
            return BaeVec2d(self.X + o.X, self.Y + o.Y)

    def __sub__(self,o):
        return BaeVec2d(self.X - o.X, self.Y - o.Y)

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
        else:
            return BaeVec2d(self.X / f.X, self.Y /f.Y)

    @staticmethod
    def Dot(lh , rh):
        return lh.X * rh.X + lh.Y * rh.Y

class BaeVec3d(BaeVec2d):
    def __init__(self, x=0,y=0,z=0):
        super().__init__(x,y)
        self._z = z

    @property
    def Z(self):
        return self._z

    @property
    def Length(self):
        return math.sqrt(self.X*self.X+self.Y*self.Y+self.Z*self.Z)
    
    def Normalize(self):
        len = self.Length
        self._x = self._x / len
        self._y = self._y / len
        self._z = self._z / len
        return self

    def __add__(self,o):
        return BaeVec3d(self.X + o.X, self.Y + o.Y, self.Z + o.Z)

    def __iadd__(self,o):
        if isinstance(o, float):
            return BaeVec3d(self.X + o, self.Y + o, self.Z + o)
        else:
            return BaeVec3d(self.X + o.X, self.Y + o.Y, self.Z + o.Z)

    def __sub__(self,o):
        return BaeVec3d(self.X - o.X, self.Y - o.Y, self.Z - o.Z)
    
    def __isub__(self,o):
        if isinstance(o, float):
            return BaeVec3d(self.X - o, self.Y - o, self.Z - o)
        else:
            return BaeVec3d(self.X - o.X, self.Y - o.Y, self.Z - o.Z)

    def __mul__(self, f):
        if isinstance(f, float):
            return BaeVec3d(self.X * f, self.Y * f, self.Z * f )
        else:
            return BaeVec3d(self.X * f.X, self.Y * f.Y, self.Z * f.Z )
    
    def __truediv__(self, f):
        return BaeVec3d(self.X / f, self.Y /f, self.Z / f)

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

    @staticmethod
    def clamp(v,b,t):
        """
        clamp value v at: b <= v <= t
        """
        return max(b, min(v,t))
    