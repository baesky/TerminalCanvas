import baeshade as bs

GRAY = bs.baeColorPallette.getGrayScale
RGB = bs.baeColorPallette.RGB

# set a buffer
bs.setBuffer(46, 23)
bgcolor = GRAY(3)


#for i in range(6):
#    for j in range(6):
#        bs.draw(j,i,RGB(i * 255/6,0,j * 255/6))

def ps(x,y):
    if x < 6 and y < 6:
        return RGB(x * 255/6,0,y * 255/6)
    else:
        return RGB(0,0,0)

bs.presentation(bgcolor, shader=ps)





#for i in range(int(15)):
#    print('\x1b[48;5;%dm' % (i) + "a" * int(46) + '\x1b[0m' )


#delta = 0
#idx = 0
#while True:
#    first_time = datetime.datetime.now()
#    c = idx % 7
#    for i in range(int(height)):
#        print('\x1b[6;30;%dm' % (c + 40) + " " * int(width) + '\x1b[0m' )
#    later_time = datetime.datetime.now()
#    delta = (later_time - first_time).total_seconds() * 1000
    #print(delta)
#    if(delta <1.0):
#        sleep(1.0 - delta)
#        delta = 0    
#    idx = idx + 1

#print("\x1b[48;5;$120m   aaaa\x1b[0m") 

#print('\x1b[6;30;42m' + '            ' + '\x1b[0m')