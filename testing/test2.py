from pyo import *
import mapper

s = Server(audio='jack').boot()
s.start()

a = BrownNoise()
b = Biquadx(a, freq=[200, 400, 800, 1600, 3200, 6400], q=10, type=2).out()

def freq_handler(sig, id, val, timetag):
    try:
        b.setFreq( val )
    except:
        print 'exception'
        print sig, val

dev = mapper.device("biquad")
dev_input = dev.add_input( "/Q", 1, "i", None, 1, 500, lambda s, i, f, t: b.setQ(f) )
dev_input = dev.add_input( "/pitch1", 1, "i", None, 20, 15000, freq_handler )

while 1:
    dev.poll(0)
