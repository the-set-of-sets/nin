# 6.18.2019
# Old code
# ----------------------
# These are slow bits of code which I replaced by faster bits of code.
# I am keeping this in a separate file because I do not trust my git skills.
# --------------------------------------

def dist(a,b):
    '''Input: a,b (both tuples of integers)
        Computes distance^2 between a,b'''
    a1, a2 = a[0], a[1]
    b1, b2 = b[0], b[1]
    return (b1 - a1)**2 + (b2 - a2)**2 + (b1-a1)*(b2-a2)

def is_colinear(a,b,c):
    '''Input: a,b,c (tuples of integers)
        Computes whether a,b,c lie on a line.'''
    a1, a2 = a[0], a[1]
    b1, b2 = b[0], b[1]
    c1, c2 = c[0], c[1]
    return (b2 - a2)*(c1 - a1) == (c2 - a2)*(b1 - a1)

def equal(x,y):
    return abs(x-y) < epsilon

def is_circle(a,b,c,d):
    '''Input: a,b,c,d (tuples of integers)
        Computes whether a,b,c,d lie on a circle.
        Uses the fact that AC * BD = AB*CD + BC*AD iff ABCD is on circle.'''
    diag1 = math.sqrt( dist(a,c) * dist(b,d) )
    diag2 = math.sqrt( dist(a,b) * dist(c,d) )
    diag3 = math.sqrt( dist(b,c) * dist(a,d) )
    max_diag = max( diag1, diag2, diag3 )
    others = diag1 + diag2 + diag3 - max_diag
    return equal(max_diag, others)

def is_general_position(c):
    '''Input: c, a list of points (tuples of integers)
        NOTE: We assume inductively that if c = [c1, ..., cn], that c1, ..., cn-1 are already in general position.'''
    last = c[-1]
    for a,b in itertools.combinations(c[:-1], 2):
        if is_colinear(a,b,last):
            return False
    for a,b,d in itertools.combinations(c[:-1], 3):
        if is_circle(a,b,d,last):
            return False
    return True
# ------------------------------------
