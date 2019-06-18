# 6.17.2019
# Sara Fish
# Description: Searches arbitrary lattice in arbitrary metric for crescent configs. Right now, set to triangle lattice and Euclidean metric, with the goal of making sure we can't get n = 9.

# USAGE INSTRUCTIONS:
# 0. Feel free to talk to me / force me to explain parts. I didn't write enough comments, sorry.
# 1. When importing nin.py, it should take < 10s. This is intended, it's because is_circle takes a while to compute.
# 2. Run the function find_crescent_set(n), where n is the size of the crescent set we want.
# 3. If the function returns "Could not find crescent set. Try a bigger grid.", then increase the global variable LATT_SIZE, re-import nin.py, and try again.
# 4. The cases n <= 7 run quickly on LATT_SIZE = 5. The case n = 8 takes 13s and then works on LATT_SIZE = 6.

# CODE NOTES:
# Inefficiencies:
# TODO Replace is_circle (which currently uses sqrt, expensive) with a faster algorithm. Maybe use the determinant formula
# - has_crescent_dist is currently written really inefficiently. I should fix that. (However, according to cProfile, to compute n=8, has_crescent_dist takes 1s and is_general_position takes 6s, so I should really be focusing on is_general_position.)
# 
# Fixed inefficiencies:
# - FIXED. instead of dist function, precompute all of the distances. Can even do this for lines, and circles. (This is not hard for small grid sizes. For large grid sizes, maybe cache a small thing and find a way how to "reduce")
# -------------- This fix cut the runtime (for n=8) down from 60s to 13s. Yay!

##################### 

LATT_SIZE = 9
GEOMETRY = 0 
# Euclidean = 0
# Taxicab = 1

import math
import itertools
import time
epsilon = 0.001

# For Euclidean metric (GEOMETRY = 0), the triangular lattice looks like this
#For example, dist[ (0,0) + (1,1) ] is 3 (because it returns dist squared.)
"""
  *     *       *      *

     *      *      *       *
(0,1)  (1,1)
  *     *      *       *
  
*    *     *      *
(0,0)(1,0)
"""

# For taxicab metric (GEOMETRY = 1), the lattice is square.
# For example, dist[ (0,0) + (1,1) ] is 2.
"""
*    *    *    *    *
(0,1) (1,1)
*    *    *    *    *
     |
*----*    *    *    *
(0,0) (1,0)
"""


######### INITIALIZATION METHODS

def init_euclidean():
    print("Initializing distances...")
    dist = dict()
    for a1,a2,b1,b2 in itertools.product(range(LATT_SIZE), repeat=4 ):
        dist[(a1,a2,b1,b2)] = (b1 - a1)**2 + (b2 - a2)**2 + (b1-a1)*(b2-a2)

    print("Initializing lines...")
    is_colinear = dict()
    for a1,a2,b1,b2,c1,c2 in itertools.product(range(LATT_SIZE), repeat=6 ):
        is_colinear[(a1,a2,b1,b2,c1,c2)] = (b2 - a2)*(c1 - a1) == (c2 - a2)*(b1 - a1)

    print("Initializing circles...")
    is_circle = dict()
    for a1,a2,b1,b2,c1,c2,d1,d2 in itertools.product(range(LATT_SIZE), repeat=8 ):
        diag1 = math.sqrt( dist[(a1,a2,c1,c2)] * dist[(b1,b2,d1,d2)] )
        diag2 = math.sqrt( dist[(a1,a2,d1,d2)] * dist[(b1,b2,c1,c2)] )
        diag3 = math.sqrt( dist[(a1,a2,b1,b2)] * dist[(c1,c2,d1,d2)] )
        max_diag = max( diag1, diag2, diag3 )
        others = diag1 + diag2 + diag3 - max_diag
        is_circle[(a1,a2,b1,b2,c1,c2,d1,d2)] = abs(max_diag - others) < epsilon # testing if floating point equal
    return dist, is_colinear, is_circle

def init_taxicab():
    print("Initializing distances...")
    dist = dict()
    for a1,a2,b1,b2 in itertools.product(range(LATT_SIZE), repeat=4 ):
        dist[(a1,a2,b1,b2)] = (b1 - a1) + (b2 - a1)

    print("Initializing lines...")
    is_colinear = dict()
    for a1,a2,b1,b2,c1,c2 in itertools.product(range(LATT_SIZE), repeat=6 ):
        is_colinear[(a1,a2,b1,b2,c1,c2)] = (b2 - a2)*(c1 - a1) == (c2 - a2)*(b1 - a1)

    print("Initializing circle...")
    is_circle = dict()
    #TODO hmmm

######## INITIALIZATION ##########
# This block of code is run each time when the file is imported.

start_init_time = time.time()

if GEOMETRY == 0:# Euclidean
    # LATT_SIZE = 6 takes 3s
    # LATT_SIZE = 7 takes 10s
    # LATT_SIZE = 9 takes 70s
    # LATT_SIZE = 10 nearly crashed my (old) computer
    dist, is_colinear, is_circle = init_euclidean()
elif GEOMETRY == 1:# Taxicab
    dist, is_colinear, is_circle = init_taxicab()
else:
    print("Invalid geometry specified.")

print("Total init time: ", time.time() - start_init_time)

##################################

############# COMPUTING CRESCENT SETS METHODS ############

def is_general_position(c):
    '''Input: c, a list of points (tuples of integers)
        NOTE: We assume inductively that if c = [c1, ..., cn], that c1, ..., cn-1 are already in general position.'''
    last = c[-1]
    for a,b in itertools.combinations(c[:-1], 2):
        if is_colinear[a+b+last]:
            return False
    for a,b,d in itertools.combinations(c[:-1], 3):
        if is_circle[a+b+d+last]:
            return False
    return True

def increment_point(a):
    '''Input: a (tuple of integers)'''
    if a[0] >= LATT_SIZE or a[1] >= LATT_SIZE:
        return None #not valid point in lattice
    if a[1] == LATT_SIZE - 1:
        if a[0] == LATT_SIZE - 1:
            return None # a was max point, so no successor
        else:
            return (a[0] + 1, 0)
    else:
        return (a[0], a[1] + 1)


def has_crescent_dist(c):
    '''Input: c, a list of points (tuples of integers)
    Assuming the points are in general position, this counts the distances between them and sees whether they satisfy the crescent condition. I.e., one distance appears 1x, one 2x, ... up to n-1x., where n is the number of points.'''
    n = len(c)
    dis = distance_set(c)
    return set(dis.values() ) == set(range(1,n))

def distance_set(c):
    '''Input: c, a list of points (tuples of integers)
        Returns a dict with its distances.'''
    dis = dict()
    for a,b in itertools.combinations(c, 2):
        d = dist[a+b]
        if d in dis.keys():
            dis[d] += 1
        else:
            dis[d] = 1
    return dis

def find_crescent_set(n):
    '''Input: n (positive integer)
       Output: crescent set of size n'''
    start_time = time.time()
    current_set = []
    next_to_add = (0,0)
    while next_to_add != None:
        # print(current_set, next_to_add)
        current_set.append(next_to_add)
        is_bad_set = False
        if not is_general_position(current_set):
            is_bad_set = True
        else:
            if len(current_set) >= n:
                if has_crescent_dist(current_set):
                    total_time = time.time() - start_time
                    print("Time taken: ",total_time)
                    print("Distance set is: ", distance_set(current_set) )
                    print("The pairs are of the form (distance^2: frequency).\n")
                    print("The coordinates of the points in the triangle lattice are:")
                    return current_set
                else:
                    is_bad_set = True
            else:
                next_to_add = increment_point(next_to_add)
                if next_to_add == None:
                    is_bad_set = True
        if is_bad_set:
            have_incremented = False
            while not have_incremented and current_set != []:
                next_to_add = increment_point(current_set.pop())
                if next_to_add != None:
                    have_incremented = True
    print("Could not find crescent set. Try a bigger grid.")

################ TEST FUNCTION ################

def test():
    '''Test function.'''
    a = (0,0)
    b = (1,1)
    c = (2,3)
    d = (3,5)
    circ1 = (0,1)
    circ2 = (1,0)
    circ3 = (2,0)
    circ4 = (1,2)
    print("a =",a)
    print("b =",b)
    print("c =",c)
    print("d =",d)
    print("circ1 =",circ1)
    print("circ2 =",circ2)
    print("circ3 =",circ3)
    print("circ4 =",circ4)
    things_to_test = ["dist[a+b]", "dist[c+d]","is_colinear[a+b+c]", "is_colinear[b+c+d]", "is_circle[circ1+circ2+circ3+circ4]","is_circle[a+b+c+d]", "increment_point(d)","is_general_position([a,b,c,d])","is_general_position([b,c,d,a])", "is_general_position([circ1,circ2,circ3,circ4])"]
    for command in things_to_test:
        print(command,"= ",end='')
        exec("print("+command+")")


