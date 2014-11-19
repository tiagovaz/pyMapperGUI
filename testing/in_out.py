import mapper

def freq_handler(sig, id, val, timetag):
    pass

def setup(d):
    dev_input = dev.add_input( "/Q", 1, "f", None, 1, 500, lambda s, i, f, t: b.setQ(f) )
    dev_input = dev.add_input( "/pitch", 1, "f", None, 20, 15000, freq_handler )
    dev_output = dev.add_output( "/x", 1, "f", None, 20, 15000)
    dev_output = dev.add_output( "/y", 1, "f", None, 20, 15000)

dev = mapper.device("device")
setup(dev)

while 1:
    dev.poll(10)
