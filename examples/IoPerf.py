import sys
import baeshade as bs
import os

util = bs.BaeshadeUtil

#buff = '\x1b[48;5;10m\x1b[0m'

"""
perf1 = util.Stopwatch()
for x in range(5000):
    print(buff,end="")


print('',flush=True)
t1 = perf1.stop()
print('print: %f ms' % (t1))
"""


# perf2 = util.Stopwatch()
# for x in range(5000):
#     sys.stdout.write(buff)

# sys.stdout.flush()
# t2 = perf2.stop()

# print('stdout: %f ms' % (t2))


"""
st = str.encode(buff)
perf3 = util.Stopwatch()
for x in range(5000):
    os.write(1,st)

t3 = perf3.stop()
sys.stdout.flush()
print('os.write: %f ms' % (t3))
"""

bufflen = 261851
large_buff = ['a'] * bufflen
large_buff = ''.join(large_buff)
perf2 = util.Stopwatch()
testNum = 10
calcTimes = [0]*testNum

#sys.stdout.reconfigure(line_buffering=False)
import io
buffer_size = 1024
buffered_stdout = io.TextIOWrapper(sys.stdout.buffer, write_through=True, line_buffering=False)

# 将 buffered_stdout 设置为新的标准输出
sys.stdout = buffered_stdout

for x in range(testNum):
    perf2.reset()
    pice = 700
    interval = 2048#bufflen // pice
    for i in range(0, bufflen, interval):
        #sys.stdout.buffer.write(large_buff[i:i+interval].encode('UTF-8'))
        sys.stdout.write(large_buff[i:i+interval])
        #os.write(1,large_buff[i:i+interval])
    
    calcTimes[x] = perf2.stop()*1000

#sys.stdout.buffer.write('test writing')

print(f'total: {testNum}')
print(f'time: {calcTimes}')