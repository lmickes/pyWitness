from numba import jit, float64, int32, int64
from numba.experimental import jitclass
import random
import numpy
import time

spec = [
    ('lureMean', float64),
    ('lureSigma', float64),
    ('targetMean', float64),
    ('targetSigma', float64),
    ('lineupSize',int32),
    ('ls',float64[:]),
    ('ts',float64[:]),
    ('i',int32),
    ('j', int32),
    ('nsamples',int32),
    ('numberConditions',int32),
    ('thresholds',float64[:]),
    ('fid',float64[:]),
    ('tid',float64[:]),
    ('m',float64)

]

@jitclass(spec)
class ModelFitsMonteCarlo :
    def __init__(self):
        self.lureMean = 0
        self.lureSigma = 1.0
        self.targetMean = 1.0
        self.targetSigma = 1.0
        self.lineupSize = 6
        self.numberConditions = 10
        self.thresholds = numpy.array([0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25, 2.5,2.75])
        self.fid = numpy.zeros(len(self.thresholds))
        self.tid = numpy.zeros(len(self.thresholds))

    def generate(self, nsamples):

        for i in range(nsamples) :
            ls = numpy.random.normal(self.lureMean, self.lureSigma,self.lineupSize-1)
            ts = numpy.random.normal(self.targetMean, self.targetSigma,1)

            lm = ls.max()

            if lm > ts:
               tp = False
               m  = lm
            else :
               tp = True
               m  = ts[0]

            for j in range(0,len(self.thresholds)) :
                if  m < self.thresholds[j] :
                    if tp :
                        self.tid[j] += 1
                        break
                    else :
                        self.fid[j] += 1
                        break




