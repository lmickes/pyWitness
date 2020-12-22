import numpy as _np
from scipy import integrate as _integrate
from scipy import optimize as _optimize
from scipy.stats import norm as _norm
import matplotlib.pyplot as _plt

class ModelFitIndependentObservation :
    def __init__(self, processedData) : 
        self.processedData    = processedData 
        self.numberConditions = processedData.numberConditions()
        self.lineupSize       = processedData.lineupSize
        self.numberTPLineups  = processedData.numberTPLineups
        self.numberTALineups  = processedData.numberTALineups
        self.pred_rates       = processedData.data_rates.copy()           # copy the processed data rates for a prediction data frame
        self.pred_rates.iloc[:,:] = 0.0
        self.iteration        = 0
        
        # parameters 
        self.lureMean    = 0.0
        self.lureSigma   = 1.0
        self.targetMean  = 1.0
        self.targetSigma = 1.0
        self.thresholds  = _np.linspace(self.lureMean, self.targetMean, self.numberConditions) # linearly spread the initial thresholds 
        # _np.array([1.1602,1.6850,2.2577]) #_np.linspace(self.lureMean, self.targetMean, self.numberConditions) # linearly spread the initial thresholds 

    def setParameters(self ) : 
        pass

    def calculateRates(self) :
        
        # target ID in target present lineups 
        def probTargetIDTargetPresent(x) :
            return _norm.cdf(x,self.lureMean, self.lureSigma)**(self.lineupSize-1)*_norm.pdf(x,self.targetMean, self.targetSigma)
        
        def probTargetIDTargetPresentIntegral(x1, x2) :
            return _integrate.quad(probTargetIDTargetPresent,x1,x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x) : 
            return _norm.cdf(x,self.lureMean, self.lureSigma)**(self.lineupSize-2)*_norm.pdf(x,self.lureMean, self.lureSigma)*_norm.cdf(x,self.targetMean, self.targetSigma)

        def probFillerIDTargetPresentIntegral(x1, x2) :
           return _integrate.quad(probFillerIDTargetPresent,x1,x2)[0]

        # filler ID (suspect ID) in target absent lineups 
        def probFillerIDTargetAbsentIntegral(x1) :
            return _norm.cdf(x1)**self.lineupSize

        # loop over conditions 
        p1 = [] 
        p2 = [] 
        p3 = [] 

        for c in self.thresholds : 
            p1.append(probTargetIDTargetPresentIntegral(c,15))
            p2.append(probFillerIDTargetPresentIntegral(c,15))
            p3.append(probFillerIDTargetAbsentIntegral(c))

        p1 = _np.array(p1)
        p2 = _np.array(p2)
        p3 = _np.array(p3)
        
        p2 = (self.lineupSize-1)*p2
        p3 = 1.0 - p3

        p1nc = _np.zeros(self.numberConditions)
        p2nc = _np.zeros(self.numberConditions)
        p3nc = _np.zeros(self.numberConditions)

        for i in range(0,self.numberConditions-1) :
            p1nc[i] = p1[i] - p1[i+1]
            p2nc[i] = p2[i] - p2[i+1]
            p3nc[i] = p3[i] - p3[i+1]
        
        p1nc[-1] = p1[-1]
        p2nc[-1] = p2[-1]
        p3nc[-1] = p3[-1]

        #print(p1nc)
        #print(p2nc)
        #print(p3nc)        
        # print(self.numberTPLineups, self.numberTALineups)

        self.pred_TP_SuspectID = p1nc*self.numberTPLineups
        self.pred_TP_FillerID  = p2nc*self.numberTPLineups
        self.pred_TA_FillerID  = p3nc*self.numberTALineups

        self.pred_TP_NoID = self.numberTPLineups - self.pred_TP_SuspectID.sum() - self.pred_TP_FillerID.sum()
        self.pred_TA_NoID = self.numberTALineups - self.pred_TA_FillerID.sum()


        #print(self.pred_TP_SuspectID, self.pred_TP_SuspectID.sum())
        #print(self.pred_TP_FillerID,  self.pred_TP_FillerID.sum())
        #print(self.pred_TA_FillerID,  self.pred_TA_FillerID.sum())    
        #print(self.pred_TP_NoID,self.pred_TA_NoID)
        
    def chiSquared(self, params) :

        params = _np.array(params)

        self.thresholds  = params[0:self.numberConditions]
        # self.lureSigma   = params[self.numberConditions]
        self.targetMean  = params[self.numberConditions+0]
        self.targetSigma = params[self.numberConditions+1]
        
        print('iteration',self.iteration)
        print('params',params)

        self.calculateRates()

        self.chi1 = 0 
        self.chi2 = 0
        self.chi3 = 0
        self.chi4 = 0
        self.chi5 = 0
        for i in range(0,self.numberConditions) :
            self.chi1 = self.chi1 + (self.processedData.data_pivot.loc['targetAbsent' ,'fillerId'][i]  - self.pred_TA_FillerID[i])**2 /self.pred_TA_FillerID[i]
            self.chi2 = self.chi2 + (self.processedData.data_pivot.loc['targetPresent','suspectId'][i] - self.pred_TP_SuspectID[i])**2/self.pred_TP_SuspectID[i]
            self.chi3 = self.chi3 + (self.processedData.data_pivot.loc['targetPresent','fillerId'][i]  - self.pred_TP_FillerID[i])**2 /self.pred_TP_FillerID[i]

        self.chi4 = (self.processedData.data_pivot.loc['targetAbsent' ,'rejectId'].sum() - self.pred_TA_NoID)**2/self.pred_TA_NoID
        self.chi5 = (self.processedData.data_pivot.loc['targetPresent','rejectId'].sum() - self.pred_TP_NoID)**2/self.pred_TP_NoID

        self.chiSqred = self.chi1 + self.chi2 + self.chi3 + self.chi4 + self.chi5

        print('chi2',
              self.chi1,
              self.chi2,
              self.chi3,
              self.chi4,
              self.chi5,
              self.chiSqred)

        self.iteration = self.iteration+1
        return self.chiSqred

    def fit(self) : 
        x0 = [1.16,1.68,2.23,1.0,1.1]

        def chiSquared(x) : 
            return self.chiSquared(x)
        print(_optimize.minimize(chiSquared, x0, method='Nelder-Mead'))

    def plotModelThreshold(self, threshold = 0, xlow = -5, xhigh = 5) : 
        x      = _np.linspace(xlow, xhigh,200) 
        lure   = _norm.pdf(x,self.lureMean, self.lureSigma)
        target = _norm.pdf(x,self.targetMean, self.targetSigma)
        
        _plt.plot(x,lure)
        _plt.plot(x,target)
        _plt.axvline(threshold)

        _plt.xlabel("Memory strength")
        _plt.ylabel("Probability")
