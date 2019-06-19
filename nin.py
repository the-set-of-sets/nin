# 6.17.2019
# Sara Fish
# Description: Searches arbitrary lattice in arbitrary metric for crescent configs. Right now, set to triangle lattice and Euclidean metric, with the goal of making sure we can't get n = 9.

# USAGE INSTRUCTIONS:
# 0. Feel free to talk to me / force me to explain parts. I didn't write enough comments, sorry.
# 1. When importing nin.py, it should take < 10s. This is intended, it's because is_circle takes a while to compute.
# 2. Run the function find_crescent_set(n), where n is the size of the crescent set we want.
# 3. If the function returns "Could not find crescent set. Try a bigger grid.", then increase the global variable LATT_SIZE, re-import nin.py, and try again.
# 4. The cases n <= 7 run quickly on LATT_SIZE = 5. The case n = 8 takes 8s and then works on LATT_SIZE = 6.

# CODE NOTES:
# Inefficiencies:
# - has_crescent_dist is currently written really inefficiently. I should fix that. (However, according to cProfile, to compute n=8, has_crescent_dist takes 1s and is_general_position takes 6s, so I should really be focusing on is_general_position.)
# 
# Fixed inefficiencies:
# - FIXED. instead of dist function, precompute all of the distances. Can even do this for lines, and circles. This is not hard for small grid sizes. For large grid sizes, maybe cache a small thing and find a way how to "reduce". (This fix cut the runtime (for n=8) down from 60s to 13s. Yay!)
# - FIXED. is_circle function was expensive. Precomputed the sqrt of all of the distances. (This cut down n=8 time from 13s to 7.5s)
# -------------- 

##################### 

LATT_SIZE = 6
GEOMETRY = 0 
# Euclidean = 0
# Taxicab = 1 (not implemented yet)

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

    #sqrt_dist = dict()
    #for pair in dist.keys():
    #    sqrt_dist[pair] = math.sqrt( dist[pair] )

    print("Initializing lines...")
    is_colinear = dict()
    for a1,a2,b1,b2,c1,c2 in itertools.product(range(LATT_SIZE), repeat=6 ):
        is_colinear[(a1,a2,b1,b2,c1,c2)] = (b2 - a2)*(c1 - a1) == (c2 - a2)*(b1 - a1)


    print("Initializing circles...")
    # https://math.stackexchange.com/questions/1304194/center-of-circle-when-three-points-in-3-space-are-given 
    # Compute circle data: 
    circle_data = dict()
    inv_circle_data = dict()
    for a1,a2,b1,b2,c1,c2 in itertools.product(range(LATT_SIZE), repeat=6 ):
        if not is_colinear[(a1,a2,b1,b2,c1,c2)]:
            a = dist[(b1,b2,c1,c2)]
            b = dist[(a1,a2,c1,c2)]
            c = dist[(a1,a2,b1,b2)]
            alpha = a * (b + c - a)
            beta = b * (c + a - b)
            gamma = c * (a + b - c)
            a1_actual = a1 + 0.5*a2 # if I cared, I would precompute these to save time.
            a2_actual = math.sqrt(3)*0.5*a2
            b1_actual = b1 + 0.5*b2
            b2_actual = math.sqrt(3)*0.5*b2
            c1_actual = c1 + 0.5*c2
            c2_actual = math.sqrt(3)*0.5*c2
            x1 = (alpha * a1_actual + beta * b1_actual + gamma * c1_actual)/(alpha + beta + gamma)
            x2 = (alpha * a2_actual + beta * b2_actual + gamma * c2_actual)/(alpha + beta + gamma)
            rad_sq = (x1 - a1_actual)**2 + (x2 - a2_actual)**2
        else:
            x1 = 0
            x2 = 0
            rad_sq = 0
        # Set the values for circle_data and inv_circle_data
        circle_data[(a1, a2, b1, b2, c1, c2)] = (x1, x2, rad_sq)
        if (x1, x2, rad_sq) in inv_circle_data.keys():
            inv_circle_data[(x1, x2, rad_sq)].append( (a1, a2, b1, b2, c1, c2) )
        else:
            inv_circle_data[(x1, x2, rad_sq)] = [(a1, a2, b1, b2, c1, c2)]
         
    # Postprocess circle data: since we don't actually need the data (x1, x2, rad), every (x1, x2, rad) is associated with a unique positive integer, and we compare those instead.
    code = 0
    for val in inv_circle_data.keys():
        for i in inv_circle_data[val]:
            circle_data[i] = code
        code += 1
    return dist, is_colinear, circle_data

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
    # LATT_SIZE = 7 takes 8s
    # LATT_SIZE = 8 takes 24s
    # LATT_SIZE = 9 takes 58s
    dist, is_colinear, circle_data = init_euclidean()
elif GEOMETRY == 1:# Taxicab
    dist, is_colinear, circle_data = init_taxicab()
else:
    print("Invalid geometry specified.")

print("Total init time: ", time.time() - start_init_time)

##################################

############# COMPUTING CRESCENT SETS METHODS ############

def is_circle(a,b,c,d):
    '''Input: a,b,c,d points (tuples of integers)
    Output: True if lie on circle, False otherwise.'''
    return circle_data[a+b+c] == circle_data[a+b+d]

def is_general_position(c):
    '''Input: c, a list of points (tuples of integers)
        NOTE: We assume inductively that if c = [c1, ..., cn], that c1, ..., cn-1 are already in general position.'''
    last = c[-1]
    for a,b in itertools.combinations(c[:-1], 2):
        if is_colinear[a+b+last]:
            return False
    for a,b,d in itertools.combinations(c[:-1], 3):
        if is_circle(a,b,d,last):
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

################## FINDING CRESCENT SET #########
# Call this function to find a crecent set. 

def find_crescent_set(n):
    '''Input: n (positive integer)
       Output: crescent set of size n'''
    start_time = time.time()
    current_set = []
    next_to_add = (0,0)
    count = 0
    while next_to_add != None:
        count += 1
        if count % 10000000 == 0:# (prints where we are every 100s)
            print(current_set)
            print(time.time() - start_time)
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
    #things_to_test = ["dist[a+b]", "dist[c+d]","is_colinear[a+b+c]", "is_colinear[b+c+d]", "is_circle[circ1+circ2+circ3+circ4]", "is_circle[a+b+c+d]", "increment_point(d)","is_general_position([a,b,c,d])", "is_general_position([b,c,d,a])", "is_general_position([circ1,circ2,circ3,circ4])"]
    things_to_test = ["circle_data[circ1+circ2+circ3]", "circle_data[circ1+circ2+circ4]", "circle_data[b+c+d]", "is_circle(circ1,circ2,circ3,circ4)"]
    for command in things_to_test:
        print(command,"= ",end='')
        exec("print("+command+")")


