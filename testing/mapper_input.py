from pyo import *
import mapper
from Audio import DarkAtmosphere, Wind, MyFM

s = Server(audio="jack", sr=44100, buffersize=512)
s.boot()

s.start()

dark1 = DarkAtmosphere()
dark2 = DarkAtmosphere()
dark3 = DarkAtmosphere()
dark4 = DarkAtmosphere()
wind = Wind(.5)
myfm = MyFM()

dark1.out()
dark2.out()
dark3.out()
dark4.out()
wind.out()
myfm.out()

dev1 = mapper.device("Dark")
dev2 = mapper.device("Dark")
dev3 = mapper.device("Dark")
dev4 = mapper.device("Dark")

# dev input 1
dev1.add_input( "/pitch1", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark1.setPitch(f, f*1.01) )
dev1.add_input( "/pitch2", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark1.setPitch(f, f*1.10) )

dev2.add_input( "/pitch1", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark2.setPitch(f, f*1.01) )
dev2.add_input( "/pitch2", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark2.setPitch(f, f*1.10) )

dev3.add_input( "/pitch1", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark3.setPitch(f, f*1.01) )
dev3.add_input( "/pitch2", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark3.setPitch(f, f*1.10) )

dev4.add_input( "/pitch1", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark4.setPitch(f, f*1.01) )
dev4.add_input( "/pitch2", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark4.setPitch(f, f*1.10) )

# dev input 2
#dev2.add_input( "/feedback", 1, "f", "Hz", 0, 1, lambda s, i, f, t: dark2.setFeedback(f) )

# dev input 3
#dev3.add_input( "/amp", 1, "f", None, 0, 1, lambda s, i, f, t: wind.setAmp(f) )
#
#dev4.add_input( "/index", 1, "f", None, 0, 20, lambda s, i, f, t: myfm.setIndex(f) )
#dev4.add_input( "/ratio", 1, "f", None, 0.01, 4, lambda s, i, f, t: myfm.setRatio(f) )
#dev4.add_input( "/amp", 1, "f", None, 0, 1, lambda s, i, f, t: myfm.setAmp(f) )
#dev4.add_input( "/pitch", 1, "f", None, 100, 600, lambda s, i, f, t: myfm.setPitch(f) )

# dev input 4
while True:
    dev1.poll(1)
    dev2.poll(1)
    dev3.poll(1)
    dev4.poll(1)
