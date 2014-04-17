#!/usr/bin/env python
# encoding: utf-8

from pyo import *
import mapper

s = Server(audio="jack", sr=44100, buffersize=512).boot()

osc_bundle = ['/om1/x',
              '/om1/y',
              '/om1/z',
              '/om2/x',
              '/om2/y',
              '/om2/z']

s.start()

om1_dev = mapper.device("om")
om2_dev = mapper.device("om")

om1_x = om1_dev.add_output("/x", 1, 'f', None, -1000, 1000)
om1_y = om1_dev.add_output("/y", 1, 'f', None, -1000, 1000)
om1_z = om1_dev.add_output("/z", 1, 'f', None, -1000, 1000)

om2_x = om2_dev.add_output("/x", 1, 'f', None, -1000, 1000)
om2_y = om2_dev.add_output("/y", 1, 'f', None, -1000, 1000)
om2_z = om2_dev.add_output("/z", 1, 'f', None, -1000, 1000)

def osc_handler(address, args):
    if address == '/om1/x':
        print args
        om1_x.update(args)
    elif address == '/om1/y':
        om1_y.update(args)
    elif address == '/om1/z':
        om1_z.update(args)
    if address == '/om2/x':
        om2_x.update(args)
    elif address == '/om2/y':
        om2_y.update(args)
    elif address == '/om2/z':
        om2_z.update(args)

a = OscDataReceive(9000, osc_bundle, osc_handler)

while True:
    om1_dev.poll(1)
    om2_dev.poll(1)
