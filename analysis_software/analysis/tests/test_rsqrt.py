"""This is a Python transcription of the famous Quake III "fast inverse
square root" function. Run the script to see a quick comparison with an
"exact" square root.
"""

import struct
import math
import numpy as np
import time

# From:
# http://stackoverflow.com/a/14431225/39182
def float2bits(f):
    """Convert a float to an int with the same bits."""
    s = struct.pack('>f', f)
    return struct.unpack('>l', s)[0]


def bits2float(b):
    """Reinterpret the bits of an int as a float."""
    s = struct.pack('>l', b)
    return struct.unpack('>f', s)[0]


# Transcribed from the original C:
# https://en.wikipedia.org/wiki/Fast_inverse_square_root
def Q_rsqrt(number):
    """The fast inverse square root function."""
    threehalfs = 1.5

    x2 = number * 0.5
    y = number
    i = float2bits(y)  # evil floating point bit level hacking
    i = 0x5f3759df - (i >> 1)  # what the fuck?
    y = bits2float(i)
    y = y * (threehalfs - (x2 * y * y))  # 1st iteration
    # y = y * (threehalfs - (x2 * y * y))  # 2nd iteration, this can be removed

    return y


def rsqrt(number):
    """A native "exact" x^{-1/2}."""
    return 1 / math.sqrt(number)

def rsqrt_numpy(number):
    """A numpy "exact" x^{-1/2}."""
    return np.reciprocal(np.sqrt(number))

def rsqrt_numpy0(number):
    
    return 1 / np.sqrt(number)

def rsqrt_numpy_math(number):
    
    return np.reciprocal(math.sqrt(number))


def compare(number):
    """Get the absolute error of the fast inverse square root function
    relative to an exact baseline.
    """
    return abs(rsqrt(number) - Q_rsqrt(number))


if __name__ == '__main__':
    #print(500, compare(500.0))
    #print(0.001, compare(0.001))
    
    n = 10000000
    
    t0 = time.time()
    for i in range(n):
        a = rsqrt(float(n))
    
    t1 = time.time()
    print("Time math = " + str(t1-t0))

    t0 = time.time()
    for i in range(n):
        a = rsqrt_numpy(float(n))
    
    t1 = time.time()
    print("Time numpy = " + str(t1-t0))
    
    t0 = time.time()
    for i in range(n):
        a = rsqrt_numpy0(float(n))
    
    t1 = time.time()
    print("Time numpy0 = " + str(t1-t0))

    t0 = time.time()
    for i in range(n):
        a = rsqrt_numpy_math(float(n))
    
    t1 = time.time()
    print("Time numpy math = " + str(t1-t0))

    t0 = time.time()
    for i in range(n):
        a = Q_rsqrt(float(n))
    
    t1 = time.time()
    print("Time Q_rsqrt = " + str(t1-t0))
