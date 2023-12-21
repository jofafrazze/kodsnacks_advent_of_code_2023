from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from functools import cache, reduce
from heapq import heapify, heappop, heappush
from itertools import combinations, permutations, product
from math import ceil, comb, factorial, gcd, isclose, lcm

from algo import a_star, custsort, merge_ranges, sssp
from constants import EPSILON, HUGE
from helpers import adjacent, between, chunks, chunks_with_overlap, columns, digits, dimensions, distance, distance_sq, eight_neighs, eight_neighs_bounded, grouped_lines, ints, manhattan, multall, n_neighs, neighs, neighs_bounded, overlap, positives, rays, rays_from_inside, words


def parse(lines):
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if lines[y][x] == 'S':
                return y, x
    

def solve_a(lines):
    h, w = dimensions(lines)
    sy, sx = parse(lines)

    seen = defaultdict(set)
    numsteps = 64

    frontier = [(0, sy, sx)]

    for steps, y, x in frontier:
        if (y, x) in seen[steps]:
            continue

        seen[steps].add((y, x))

        if steps == numsteps:
            continue

        for ny, nx in neighs_bounded(y, x, 0, h-1, 0, w-1):
            if lines[ny][nx] == '#' or (ny, nx) in seen[steps+1]:
                continue

            frontier.append((steps+1, ny, nx))


    return len(seen[numsteps])


def solve_b(lines):
    h, w = dimensions(lines)
    sy, sx = parse(lines)

    firstseens = {
        (y, x): (set(), defaultdict(list)) for y, x in product(range(h), range(w))
    }
    
    maxsteps = 2719
    n = 26501365

    thisgen = [(sy, sx)]
    totseen = set()
    nextgen = set()
    step = 0

    while step < maxsteps+1:
        if step % 100 == 0:
            print(step, maxsteps, len(totseen))
        for y, x in thisgen:
            wy, wx = y//h, x//w
            oy, ox = y%h, x%w

            if (wy, wx) not in firstseens[(oy, ox)][0]:
                firstseens[(oy, ox)][0].add((wy, wx))                
                firstseens[(oy, ox)][1][step].append((wy, wx))

            for ny, nx in neighs(y, x):
                if lines[ny%h][nx%w] == '#':
                    continue

                nextgen.add((ny, nx))
        
        thisgen = list(nextgen-totseen)
        totseen |= nextgen
        nextgen = set()
        step += 1
        
    def find_recurrence(series):
        firstdiffs = [series[i][0] - series[i-1][0] for i in range(1, len(series))]

        for skip in range(3, len(firstdiffs)//2):
            for cycle_length in range(1, len(firstdiffs)//2):
                proposal = [d for d in firstdiffs[skip:cycle_length+skip]]

                valid = True

                for i, d in enumerate(firstdiffs[skip:]):
                    if proposal[i%cycle_length] != d:
                        valid = False
                        break

                if valid:
                    return skip, len(proposal), proposal
        
    def series_analyzer(series, n):
        skip, cycle_length, cycle = find_recurrence(series)
        cycle_start = series[skip][0]
        cycle_span = sum(cycle)

        print(cycle_length, cycle_span, len(series), [s[0] for s in series], cycle)
        print()

        full_cycles = (n - cycle_start) // cycle_span
        skip_span = full_cycles * cycle_span
        cycle_index = 0
        cumskip = [cycle[0]]

        for c in cycle[1:]:
            cumskip.append(c + cumskip[-1])

        while cycle_index < cycle_length and skip_span + cumskip[cycle_index] <= n - cycle_start:
            cycle_index += 1        

        cumvalues = [s[2] for s in series[skip+cycle_index:len(series):cycle_length]]
        basediff = cumvalues[1] - cumvalues[0]
        extradiff = cumvalues[3] + cumvalues[1] - 2 * cumvalues[2]
        magicdiff = cumvalues[2] - cumvalues[1] - basediff - extradiff        
        extradiffcount = (full_cycles - 1 + (full_cycles-1)**2) // 2

        val = cumvalues[0] + basediff * full_cycles + extradiff * extradiffcount + (full_cycles - 1) * magicdiff

        return val
        
    cumcumsum = 0
    cumcumsum2 = 0

    for y, x in product(range(h), range(w)):   
        cumsum = 0
        k = (y, x)
        v = firstseens[(k)]
        
        if not v[1]:
            continue

        series = []
        
        for kk, vv in v[1].items():
            if kk % 2 == maxsteps % 2:
                cumsum += len(vv)
                series.append((kk, len(vv), cumsum))

        cumcumsum2 += series_analyzer(series, n)

        cumcumsum += cumsum
            
    return cumcumsum2


def main():
    lines = []

    with open('21.txt') as f:
        for line in f.readlines():
            lines.append(line.rstrip())
            
    return (solve_a(lines), solve_b(lines))


if __name__ == '__main__':
    print(main())