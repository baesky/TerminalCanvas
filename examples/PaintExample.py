import baeshade as bs
import datetime as dt
from time import sleep

#for i in range(int(15)):
#    print('\x1b[48;5;%dm' % (i) + "a" * int(46) + '\x1b[0m' )

height = 1
width = 42

delta = 0
idx = 0
#print('\x1b[=18H]')

#for i in range(256):+ "▀" * int(width)
 #   print('\x1b[48;2;%d;%d;%dm' % (i,i,i) + " " * int(width) + '\x1b[0m',)
print('\x1b[48;2;%d;%d;%dm' % (128,0,0) + '\x1b[38;2;%d;%d;%dm' % (0,128,0) 
      + '▀' + '\x1b[0m',end="")
print('\x1b[38;5;%dm' % (128) + '\x1b[48;5;%dm' % (64) 
      + '▀' + '\x1b[0m',end="")

while False:
    first_time = dt.datetime.now()
    c = idx % 7
    
    print('\x1b[48;5;%dm' % (c *  30) + " " * int(width) + '\x1b[0m',end="" )
    
    later_time = dt.datetime.now()
    delta = (later_time - first_time).total_seconds() * 1000
    #print(delta)
    if(delta <1.0):
        sleep(1.0 - delta)
        delta = 0    
        print('\b'*42,end="",flush=True)
        
        
    idx = idx + 1
