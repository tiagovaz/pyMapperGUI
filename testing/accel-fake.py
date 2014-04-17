#!/usr/bin/python

from pyo import *

s = Server(audio="jack").boot()

osc = OscSend(Randi(-1000, 1000), port=9000, address=['/om1/x'], host='127.0.0.1')
#osc = OscSend(Randi(500, 1500), port=8000, address=['/wacom/1/pen/O/button/1'], host='127.0.0.1')

#s.start()

s.gui(locals())
