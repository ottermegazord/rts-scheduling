import math
from functools import reduce

def _LCM(a,b): return abs(a * b) // math.gcd(a,b) if a and b else 0

def LCM(a):
    return reduce(_LCM, a)