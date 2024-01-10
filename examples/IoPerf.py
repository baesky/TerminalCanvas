import sys
import baeshade as bs
import os

util = bs.BaeshadeUtil

buff = '\x1b[48;5;10m\x1b[0m'

"""
perf1 = util.Stopwatch()
for x in range(5000):
    print(buff,end="")


print('',flush=True)
t1 = perf1.stop()
print('print: %f ms' % (t1))
"""


perf2 = util.Stopwatch()
for x in range(5000):
    sys.stdout.write(buff)

sys.stdout.flush()
t2 = perf2.stop()

print('stdout: %f ms' % (t2))


"""
st = str.encode(buff)
perf3 = util.Stopwatch()
for x in range(5000):
    os.write(1,st)

t3 = perf3.stop()
sys.stdout.flush()
print('os.write: %f ms' % (t3))
"""


