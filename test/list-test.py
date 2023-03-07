from time import perf_counter
from random import randint
import numpy as np
to = perf_counter()

l = np.array([], dtype=float)
l = []
e = [1] * 10
print(e)

t0 = perf_counter()

for i in range(10):
    #np.append(l, [randint(1, 2)] * 100)
    print(l)
    l.extend(e)
    # l.append([randint(1, 2)] * 100)
    if i % 10000 == 0:
        l = l[:-10000]

print(l)
print(t0 - perf_counter())
print(len(l))
