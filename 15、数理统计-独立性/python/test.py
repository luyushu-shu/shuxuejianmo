from core import *

print(parallel(3, 0.9))
print(parallel(3, [0.9, 0.8, 0.7]))
print(series(3, 0.1))
print(series(3, [0.1, 0.2, 0.3]))
print(vote(5, 0.1 , 0.6))
print(vote(5, 0.1, 3))
