# 6.17.2019, updated 8.7.2019
# Sara Fish
# Description: Searches arbitrary lattice in L2 for crescent configs.

# USAGE INSTRUCTIONS:
# python3 nin.py <crescent size> <grid size>

# CODE NOTES:
# Inefficiencies:
# - has_crescent_dist is currently written really inefficiently. I should fix that.
# (However, according to cProfile, to compute n=8, has_crescent_dist takes 1s
# and is_general_position takes 6s, so I should really be focusing on is_general_position.)


#####################

import math
import itertools
import time
import sys
epsilon = 0.001

# The triangular lattice looks like this
#For example, dist[ (0,0) + (1,1) ] is 3 (because it returns dist squared.)
"""
  *     *       *      *
     *      *      *       *
(0,1)  (1,1)
  *     *      *       *

*    *     *      *
(0,0)(1,0)
"""


######### INITIALIZATION METHODS

def init_euclidean(grid_size, forbid_parallelograms):
    """Precomputes <dist>, <is_colinear>, <is_circle>, <is_special>
    (Also computes sqrt_dist, which is used internally.)
    Input: <grid_size>
           <forbid_parallelograms>: If True, do not compute parallelograms
                                     If False, compute parallelograms
    Output: dist, is_colinear, is_circle, is_special
            <dist> dict, key (a1, a2, b1, b2), value dist^2 between
                    (a1, a2) and (b1, b2)
            <is_colinear> dict, key (a1,a2,b1,b2,c1,c2), value True/False
                    whether (a1, a2), (b1, b2), (c1, c2) lie on line
            <is_circle> set, contains (a1,a2,b1,b2,c1,c2,d1,d2) which lie
                    on circle
            <is_special> set, contains (a1,a2,b1,b2,c1,c2,d1,d2) which lie
                    on parallelogram"""
    print("Initializing distances...")
    dist = dict()
    for a1,a2,b1,b2 in itertools.product(range(grid_size + 1), repeat=4 ):
        dist[(a1,a2,b1,b2)] = (b1 - a1)**2 + (b2 - a2)**2 + (b1-a1)*(b2-a2)

    sqrt_dist = dict()
    for pair in dist.keys():
        sqrt_dist[pair] = math.sqrt( dist[pair] )

    print("Initializing lines...")
    is_colinear = dict()
    for a1,a2,b1,b2,c1,c2 in itertools.product(range(grid_size + 1), repeat=6 ):
        is_colinear[(a1,a2,b1,b2,c1,c2)] = (b2 - a2)*(c1 - a1) == (c2 - a2)*(b1 - a1)

    print("Initializing circles...")
    is_circle = set()
    for a1,a2,b1,b2,c1,c2,d1,d2 in itertools.product(range(grid_size + 1), repeat=8 ):
        diag1 = sqrt_dist[(a1,a2,c1,c2)] * sqrt_dist[(b1,b2,d1,d2)]
        diag2 = sqrt_dist[(a1,a2,d1,d2)] * sqrt_dist[(b1,b2,c1,c2)]
        diag3 = sqrt_dist[(a1,a2,b1,b2)] * sqrt_dist[(c1,c2,d1,d2)]
        max_diag = max( diag1, diag2, diag3 )
        others = diag1 + diag2 + diag3 - max_diag
        if abs(max_diag - others) < epsilon: # testing if floating point equal
            is_circle.add((a1,a2,b1,b2,c1,c2,d1,d2))

    is_special = set()
    if forbid_parallelograms:
        print("Initializing parallelograms...")
        for a1,a2,b1,b2,c1,c2,d1,d2 in itertools.product(range(grid_size + 1), repeat=8 ):
            # I realize this is slow but I don't care.
            # Test if ABCD is special with AB || CD, AC || BD,  AB = BC = CD
            if b2 - a2 == d2 - c2 and b1 - a1 == d1 - c1:
                if c2 - a2 == d2 - b2 and c1 - a1 == d1 - b1:
                    ab = dist[(a1,a2,b1,b2)]
                    bc = dist[(b1,b2,c1,c2)]
                    cd = dist[(c1,c2,d1,d2)]
                    if ab == bc == cd:
                        l = [a1,a2,b1,b2,c1,c2,d1,d2]
                        for r in itertools.permutations(range(4),4):
                            is_special.add(
                            (l[2*r[0]], l[2*r[0] + 1],
                             l[2*r[1]], l[2*r[1] + 1],
                             l[2*r[2]], l[2*r[2] + 1],
                             l[2*r[3]], l[2*r[3] + 1]) )
                        #is_special.add((a1,a2,b1,b2,c1,c2,d1,d2))
    return dist, is_colinear, is_circle, is_special

##################################

############# COMPUTING CRESCENT SETS METHODS ############

def is_general_position(c, forbid_parallelograms):
    """ Computes whether <c>, a list of points, lies in general position.
    General position means:
        - no 3 on a line
        - no 4 on a circle
        - if forbid_parallelograms: no 4 in special parallelogram
        (Special parallelogram is parallelogram ABCD with AB = BC = CD.)
    Input: <c>, a list of points (tuples of integers)
           <forbid_parallelograms>, True/False (whether to forbid
                parallelograms)
    Output: True/False (whether in general position)
    IMPORTANT NOTE: We assume inductively that if c = [c1, ..., cn], that
    c1, ..., cn-1 are already in general position. This function will not
    work as expected if used on an arbitrary set."""
    last = c[-1]
    for a,b in itertools.combinations(c[:-1], 2):
        if is_colinear[a+b+last]:
            return False
    for a,b,d in itertools.combinations(c[:-1], 3):
        if a+b+d+last in is_circle:
            return False
    if forbid_parallelograms:
        for a,b,d in itertools.permutations(c[:-1], 3):
            if a+b+d+last in is_special:
                return False
    return True

def increment_point(a, grid_size):
    """ Increments point <a> in <grid_size>.
    Input: <a>, point
    Output: <a> incremented in <grid_size>, if it exists, else None"""
    if a[0] > grid_size or a[1] > grid_size:
        return None #not valid point in lattice
    if a[1] == grid_size:
        if a[0] == grid_size:
            return None # a was max point, so no successor
        else:
            return (a[0] + 1, 0)
    else:
        return (a[0], a[1] + 1)


def has_crescent_dist(c):
    """ Computes whether <c>, set of points, has crescent dist.
    Crescent dist means: If c has size n, then for 1 <= i <= n - 1, the ith
    distance appears exactly i times.
    Input: <c>, a list of points
    Output: True/False (whether <c> has crescent dist )
    """
    n = len(c)
    dis = distance_set(c)
    return set(dis.values() ) == set(range(1,n))
    # return len(dis.values() ) <= n # WEAKER CONDITION

def distance_set(c):
    """ Computes the distance set of <c>
    Input: c, a list of points
    Output: dict, key distance, value multiplicity"""
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

def find_crescent_set(n, grid_size, forbid_parallelograms):
    """ Finds crescent set of size <n> in <grid_size>.
    Input: <n> (positive integer)
           <grid_size> grid size
           <forbid_parallelograms> True/False (whether to forbid special
                parallelograms)
    Output: crescent set of size n, or prints that it does not exist"""
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
        if not is_general_position(current_set, forbid_parallelograms):
            is_bad_set = True
        else:
            if len(current_set) >= n:
                if has_crescent_dist(current_set):
                    total_time = time.time() - start_time
                    print("Time taken: ",total_time)
                    print("Distance set is: ", distance_set(current_set) )
                    print("The pairs are of the form (distance^2: frequency).\n")
                    print("The coordinates of the points in the triangle lattice are:", current_set)
                    return current_set
                else:
                    is_bad_set = True
            else:
                next_to_add = increment_point(next_to_add, grid_size)
                if next_to_add == None:
                    is_bad_set = True
        if is_bad_set:
            have_incremented = False
            while not have_incremented and current_set != []:
                next_to_add = increment_point(current_set.pop(), grid_size)
                if next_to_add != None:
                    have_incremented = True
    print("Could not find crescent set. Try a bigger grid.")

################ TEST FUNCTION ################

def test():
    """Test function."""
    print(is_special)


##############################################################
##############################################################

if __name__ == "__main__":
    print_usage = False
    if len(sys.argv) <= 4:
        print_usage = True
    elif len(sys.argv) >= 4:
        mode = sys.argv[1]
        try:
            crescent_size = int(sys.argv[2])
            grid_size = int(sys.argv[3])
            forbid_parallelograms = sys.argv[4]
            if forbid_parallelograms == "y":
                forbid_parallelograms = True
            elif forbid_parallelograms == "n":
                forbid_parallelograms = False
            else:
                raise ValueError
        except ValueError:
            print_usage = True
    if not print_usage:
        if mode == "test":
            dist, is_colinear, is_circle, is_special = init_euclidean(grid_size,
                forbid_parallelograms)
            test()
        elif mode == "crescent":
            # initialization
            start_init_time = time.time()
            dist, is_colinear, is_circle, is_special = init_euclidean(grid_size,
                forbid_parallelograms)
            print("Total init time: ", time.time() - start_init_time)

            # compute crescent set
            find_crescent_set( crescent_size, grid_size, forbid_parallelograms)
    else:
        print("Usage: python3 "+sys.argv[0]+" <mode>"+" <crescent_size>"+" <grid_size>"+
        " <forbid_parallelograms>")
        print("mode: test, crescent")
        print("\t test, runs test function")
        print("\t crescent, finds crescent set")
        print("crescent_size: Size of crescent set being searched for.")
        print("grid_size: Searches grid from (0,0) to (grid_size, grid_size)")
        print("forbid_parallelograms: y or n")
        print("\t y, forbids special parallelograms")
        print("\t n, forbids special parallelograms")
        print("(A special parallelogram is ABCD with AB = BC = CD.)")
