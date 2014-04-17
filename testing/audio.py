from pyo import *

class FreqMod:
    def __init__(self, carrier=150):
        self.ratio = SigTo(0.5, time=0.05, init=0.5)
        self.index = SigTo(5, time=0.05, init=5)
        self.fm1 = FM(carrier=carrier, ratio=self.ratio, index=self.index, mul=0.3)
        self.fm2 = FM(carrier=carrier*1.01, ratio=self.ratio, index=self.index, mul=0.3)
        self.fmst = Mix([self.fm1, self.fm2], voices=2)

    def out(self):
        self.fmst.out()
        return self

    def sig(self):
        return self.fmst

    def setRatio(self, x):
        xx = x * 1.999 + 0.001
        self.ratio.value = xx

    def setIndex(self, x):
        xx = x * 20
        self.index.value = xx

if __name__ == "__main__":
    s = Server(audio="jack").boot()
    fm = FreqMod(150).out()
    harm = Harmonizer(fm.sig(), transpo=2).out()
    s.gui(locals())
