from pyo import *
from random import *

class DarkAtmosphere:
    def __init__(self, p1=.2054, p2=[.3966, .3933], chaos=.025, feedback=.5, mul=.5):
        self.r1 = Rossler(pitch=p1, chaos=.4038, stereo=True, mul=mul, add=.2)
        self.r2 = Rossler(pitch=p2, chaos=.0769, mul=self.r1*.8)
        self.amp = Fader(fadein=5, fadeout=5, dur=0)
        self.d = Delay(self.r2, feedback=.5, mul=self.amp)

    def setFeedback(self, feedback):
        self.d.feedback = feedback
        return self

    def setPitch(self, p1, p2):
        self.r1.pitch = p1
        self.r2.pitch = p2
        return self

    def setChaos(self, chaos):
        self.r1.chaos = chaos
        return self

    def out(self):
        self.d.out()
        self.amp.play()
        return self

    def tail(self):
        self.amp.stop()

    def sig(self):
        return self.d

    def stop(self):
        self.d.stop()
        self.r1.stop()
        self.r2.stop()
        return self

    def getOut(self):
        return self.amp

    def setInput(self, x, fadetime=.001):
        self.input.setInput(x, fadetime)

class MyDelay:
    """A sensor controls delay/reverb of an audio stream
       - audio1 being an Input() signal
       - audio2 being a sensor output (audio stream) from 0 to 1
       - audio3 being a sensor output (audio stream) from 40 to 800
    """
    #TODO: no mess, take fadein/out as argument
    def __init__(self, audio1, audio2=.01, audio3=40, mul=.7):
        self.lfd = Sine([.4,.3], mul=.2, add=.5)
        self.supersaw = SuperSaw(freq=[ audio3*uniform(0.94, 1.04) for i in range(10) ], detune=self.lfd, bal=0.7, mul=.1)
        self.r = Freeverb(self.supersaw, size=.94, damp=.87, bal=.9, mul=1)
        self.d2 = Delay(self.r, delay=audio2, feedback=uniform(0.95, 1), mul=.4)
        self.d2.ctrl()
        self.d3 = Delay(self.d2, delay=[.05, .1, .25, .5], feedback=.25, mul=.4)
        self.d3.ctrl()
        #self.c = Chorus(audio1, depth=[1.5,1.6], feedback=0.5, bal=0.5)
        self.r2 = Freeverb(audio1, size=.74, damp=.87, bal=.5, mul=1)
        self.d4 = Delay(self.r2, delay=audio2, feedback=uniform(0.95, 1), mul=.6)
        self.d4.ctrl()
        #self.mix = Freeverb(Mix(self.d2 + self.d3 + self.r2 + self.d4, mul=.7), size=.34, damp=.37, bal=.9, mul=.9)
        self.amp = Fader(fadein=20, fadeout=20)
        self.mix = Mix(self.d2 + self.d3 + self.r2 + self.d4, mul=self.amp*mul).out()

    def setSawFreq(self, freq):
        self.supersaw = SuperSaw(freq=[ freq*uniform(0.94, 1.04) for i in range(10) ], detune=self.lfd, bal=0.7, mul=.1)

    def setDelay(self, delay):
        self.d4.delay = delay

    def out(self):
        self.amp.play()
        return self

    def stop(self):
        self.amp.stop()
        return self

    def getOut(self):
        return self.amp

    def setInput(self, x, fadetime=.001):
        self.input.setInput(x, fadetime)

class SmoothNoise():
    def __init__(self, dur=1.3):
        self.amp = Fader(fadein=.1, fadeout=.01, dur=dur)
        self.noise = PinkNoise(self.amp*.01).mix(2).out()

    def setDur(self, dur):
        self.amp.dur = dur
        return self

    def out(self):
        self.amp.play()
        return self

    def stop(self):
        self.amp.stop()
        return self

    def getOut(self):
        return self.amp

    def setInput(self, x, fadetime=.001):
        self.input.setInput(x, fadetime)

class HighFreq():
    def __init__(self, freq=[11200, 11202], dur=.3):
        self.amp = Fader(fadein=.01, fadeout=.01, dur=dur)
        self.sine = SineLoop(freq=freq, mul=self.amp*.05).out()
        self.rev = Freeverb(self.sine, size=.84, damp=.87, bal=.9, mul=self.amp*.2).out()

    def setDur(self, dur):
        self.amp.dur = dur
        return self

    def out(self):
        self.amp.play()
        return self

    def stop(self):
        self.amp.stop()
        return self

    def getOut(self):
        return self.amp

#TODO: give random Randi freqs
class Wind():
    """Simple wind generator with Pyo"""
    def __init__(self, mul):
        # Brown noise to have less high frequency to cutoff
        self.noise = BrownNoise(mul=Randi(0.5,1))

        # This gives a factor for both the wind intensity and frequency. Intensity
        # and frequency go together in the two first filters in order to generate a
        # more natural wind. Q variation gives a kind of wind blows.
        self.j = Randi(1,1.4,Randi(.5,1))

        # Filter 1 - sort of continuos bass wind
        self.freqs1 = Randi(150, 300)
        self.q1 = Randi(1, 6)
        self.f1 = ButBP(self.noise, freq=self.freqs1, q=self.q1, mul=.2*self.j)

        # Filter 2 - main wind frequency with slow variation, following wind intensity
        self.freqs2 = [Randi(300, 400)*self.j for i in range(3)]
        self.q2 = Randi(40, 300)
        self.f2 = ButBP(self.noise, freq=self.freqs2, q=self.q2, mul=self.j*1.5)

        # Filter 3 - very high component, almost fixed in frequency
        self.freqs3 = [Randi(2990, 3000)*self.j for i in range(2)]
        self.q3 = Randi(1, 33)
        self.f3 = ButBP(self.noise, freq=self.freqs3, q=self.q3, mul=.01)

        # Filter 4 - the highest frequency wind component, also quite fixed
        self.freqs4 = [Randi(10000, 10100)*self.j for i in range(2)]
        self.q4 = Randi(10, 33)
        self.f4 = ButBP(self.noise, freq=self.freqs4, q=self.q4, mul=.01)

        # Player
        self.amp = Fader(fadein=5, fadeout=5)
        self.mix = Mix([self.f1, self.f2, self.f3, self.f4],voices=2, mul=self.amp*mul).out()

    def setAmp(self, amp):
        self.mix.mul = amp

    def out(self):
        self.amp.play()
        return self

    def stop(self):
        self.amp.stop()
        return self

    def getOut(self):
        return self.amp

class MyFM():
    def __init__(self, index=1, ratio=1, amp=.1, pitch=300):
        self.amp = amp
        self.pitch = pitch
        self.ratio = ratio
        self.index = index
        self.fm1 = FM(carrier=self.pitch, ratio=self.ratio, index=self.index, mul=self.amp*0.1).mix(1)
        self.fm2 = FM(carrier=self.pitch*1.01, ratio=self.ratio, index=self.index, mul=self.amp*0.1).mix(1)
        self.fm3 = FM(carrier=self.pitch*0.99, ratio=self.ratio, index=self.index, mul=self.amp*0.1).mix(1)
        self.fm4 = FM(carrier=self.pitch*1.04, ratio=self.ratio, index=self.index, mul=self.amp*0.1).mix(1)
        self.outmix = Mix([self.fm1, self.fm2, self.fm3, self.fm4], voices=2).out()

    def setRatio(self, r):
        self.ratio = r
        self.ratio = r
        self.ratio = r
        self.ratio = r

    def setIndex(self, index):
        self.index = self.index = self.index = self.index = index

    def setAmp(self, mul):
        self.fm1.mul = self.fm2.mul = self.fm3.mul = self.fm4.mul = mul

    def setAmp(self, pitch):
        self.pitch = pitch * random.uniform(0.97, 1.03)
        self.pitch = pitch * random.uniform(0.97, 1.03)
        self.pitch = pitch * random.uniform(0.97, 1.03)
        self.pitch = pitch * random.uniform(0.97, 1.03)

    def out(self):
        self.outmix.out()

    def stop(self):
        self.outmix.stop()
