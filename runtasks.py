#!/usr/bin/env python
# Run a few tasks for testing purposes...
from tasks import fib, add

res1 = add.delay(1,1)
res2 = add.delay(2,2)
res3 = add.delay(3,3)
f1 = fib.delay(15)
f2 = fib.delay(100)

print res1.get()
print res2.get()
print res3.get()

print f1.get()
print f2.get()
