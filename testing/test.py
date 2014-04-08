from pyo import *
from pyolib._wxwidgets import ControlSlider, BACKGROUND_COLOUR
import wx

import mapper

class MyFrame(wx.Frame):
    def __init__(self, parent, title, size, colour="#DDDDE7"):
        wx.Frame.__init__(self, parent, -1, title=title, size=size)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.dev = mapper.device("test")

        pos_y = 20 # y position for labels & slides
        s_label = 0 # integer which will generate incremented labels
        signal_id = 0 # this will be used to set the proper mapper signal

        #TODO: generate list of outputs and get their 'real' names to create the labels - duhhh
        for i in range(10): # generating lables & slides list
            self.slider = MyControlSlider(self, -60, 18, 0, pos=(45, pos_y), backColour=colour, signal_id=signal_id)
            sizer.Add(wx.StaticText(self, -1, str(s_label)+".", pos =(20, pos_y)), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            s_label += 1
            pos_y += 25
            signal_id += 1

        # mapper poll
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(milliseconds=10, oneShot=False)

    def OnTimer(self, evt):
        self.dev.poll(1)

class MyControlSlider(ControlSlider):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), size=(200,16), log=False,
                 integer=False, powoftwo=False, backColour=None, signal_id=None):

        ControlSlider.__init__(self, parent=parent, minvalue=minvalue, maxvalue=maxvalue, init=init,
                               pos=pos, size=size, log=log, outFunction=self.setMapper, integer=integer,
                               powoftwo=powoftwo, backColour=backColour)

        self.signal_id = signal_id
        self.mon = mapper.monitor()
        self.dev = self.GetParent().dev
        self.output = self.dev.add_output("/signal/"+str(self.signal_id), 1, 'f', None, -1000, 1000)

        while not self.dev.ready():
            self.dev.poll(10)
            self.mon.poll()

    def setMapper(self, value):
        self.output.update(value)

app = wx.App(False)
frame = MyFrame(None, title="testing pymapper", size=(280, 300))
frame.Show()
app.MainLoop()

