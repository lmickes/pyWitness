import numpy as _np
from scipy import integrate as _integrate
from scipy import optimize as _optimize
from scipy import interpolate as _interpolate
from scipy.stats import norm as _norm
import scipy.special as _sc
import matplotlib.pyplot as _plt
import random as _rand
import math as _math
from numba import jit


@jit(nopython=True)
def normpdf(x, mean, sigma) :
    stp = _np.sqrt(2*_np.pi)
    return 1.0/(sigma*stp)*_np.exp(-0.5*((x-mean)/sigma)**2)

def normcdf(x, mean, sigma) :
    z  = (x-mean)/sigma

    return _sc.ndtr(z)

def truncatedMean(mu, sigma, x) :
    beta = (x-mu)/sigma
    Z    = normpdf(beta,0,1)/normcdf(beta,0,1)
    return mu - sigma*Z

def truncatedVar(mu, sigma, x) :
    beta = (x-mu)/sigma
    Z    = normpdf(beta,0,1)/normcdf(beta,0,1)
    return sigma**2*(1.-Z*beta-Z**2)

class Parameter(object) : 

    def __init__(self, name, value, fixed = False) :
        self.name  = name
        self.__value = value
        self.__fixed = fixed
        self.other = None
        
    @property
    def value(self) :
        if not self.other : 
            return self.__value
        else :
            return self.other.value

    @value.setter
    def value(self,value) : 
        if not self.other :
            self.__value = value 
        else : 
            self.other.value = value

    @property 
    def fixed(self) : 
        return self.__fixed

    @fixed.setter
    def fixed(self,fixed) :
        self.__fixed = fixed

    def set_equal(self, other) : 
        self.other = other
        self.fixed = True

    def unset_equal(self):
        self.other = None
        self.fixed = False

    def __eq__(self, other) : 
        return self.value == other.value
            
    def __float__(self) :
        return self.value

    def __copy__(self) :
        new = Parameter(0)
        new.value = self.value
        return new

    def __repr__(self):

        if self.fixed :
            fixStr = "fixed"
            
            if self.other :
                fixStr = fixStr+" "+self.other.name
            
        else : 
            fixStr = "free"
            
        return self.name+" "+repr(self.value)+" ("+fixStr+")"

class ModelFit(object) :
    def __init__(self, processedData, debug = False, integrationSigma = 6) :
        self.processedData    = processedData 
        self.numberConditions = processedData.numberConditions
        self.lineupSize       = processedData.lineupSize
        self.numberTPLineups  = processedData.numberTPLineups
        self.numberTALineups  = processedData.numberTALineups
        self.pred_rates       = processedData.data_rates.copy()           # copy the processed data rates for a prediction data frame
        self.pred_rates.iloc[:,:] = 0.0
        self.iteration        = 0
        self.debug            = debug
        self.integrationSigma = integrationSigma

        # parameters 
        self.parameterNames     = []
        self.lureMean           = self.addParameter("lureMean",0.0)
        self.lureSigma          = self.addParameter("lureSigma",1.0)
        self.targetMean         = self.addParameter("targetMean",1.0)
        self.targetSigma        = self.addParameter("targetSigma",1.0)
        self.lureBetweenSigma   = self.addParameter("lureBetweenSigma",0.0)
        self.targetBetweenSigma = self.addParameter("targetBetweenSigma",0.0)

        thresholds = _np.linspace(self.targetMean.value, self.targetMean.value+self.targetSigma.value, self.numberConditions)    
        self.thresholds = [] 
        for i in range(0,self.numberConditions,1) :
            self.thresholds.append(self.addParameter("c"+str(i+1),thresholds[i]))

        self.calculateWithinSigmas()

    def addParameter(self, name, value, fixed = False) :
        self.parameterNames.append(name) 
        p = Parameter(name,value,fixed)
        setattr(self,name,p)
        return p

    def freeParameterList(self) : 
        freeParams = []
        for p in self.parameterNames : 
            p = getattr(self,p) 
            if not p.fixed :
                freeParams.append(p)

        return freeParams


    def resetParameters(self):
        self.lureMean.value = 0.0
        self.lureSigma.value = 1.0
        self.targetMean.value = 1.0
        self.targetSigma.value = 1.0
        self.lureBetweenSigma.value = 0.3
        self.targetBetweenSigma.value = 0.3

        thresholds = _np.linspace(self.targetMean.value, self.targetMean.value+self.targetSigma.value, self.numberConditions)
        for i in range(0,self.numberConditions,1) :
            getattr(self,"c"+str(i+1)).value = thresholds[i]

    def printParameters(self) : 
        for p in self.parameterNames :
            p = getattr(self,p) 
            print(p)

    def setEqualVariance(self) :
        self.lureMean.value = 0.0
        self.lureMean.fixed = True
        self.lureSigma.set_equal(self.targetSigma)
        self.targetMean.value = 1.0
        self.targetSigma.value = 1.0
        self.targetSigma.fixed = True
        self.lureBetweenSigma.set_equal(self.targetBetweenSigma)
        self.targetBetweenSigma.fixed = True
        self.targetBetweenSigma.value = 0.0
        
    def calculateWithinSigmas(self) :
        self.lureWithinSigma    = _np.sqrt(self.lureSigma.value**2   - self.lureBetweenSigma.value**2)
        self.targetWithinSigma  = _np.sqrt(self.targetSigma.value**2 - self.targetBetweenSigma.value**2)

    def calculateFrequencyForCriterion(self, c1, c2) :
        pred_c1 = self.calculateCumulativeFrequencyForCriterion(c1)
        pred_c2 = self.calculateCumulativeFrequencyForCriterion(c2)

        return pred_c2 - pred_c1

    def calculateFrequenciesForAllCriteria(self) :     
        pred_tafid_array = []
        pred_tpsid_array = []
        pred_tpfid_array = []
   
        for i in range(0,len(self.thresholds),1) : 
            if i < len(self.thresholds)-1 : 
                [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateFrequencyForCriterion(self.thresholds[i+1], self.thresholds[i])                 
            else :
                [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(self.thresholds[i]) 
                
            pred_tafid_array.append(pred_tafid)
            pred_tpsid_array.append(pred_tpsid)
            pred_tpfid_array.append(pred_tpfid)


        pred_tafid_array = _np.array(pred_tafid_array)
        pred_tasid_array = pred_tafid_array/self.lineupSize
        pred_tpsid_array = _np.array(pred_tpsid_array)
        pred_tpfid_array = _np.array(pred_tpfid_array)

        pred_tarid = self.numberTALineups - pred_tafid_array.sum()
        pred_tprid = self.numberTPLineups - pred_tpsid_array.sum() - pred_tpfid_array.sum()
 
        if self.debug :
            print('pred_tafid',pred_tafid_array)
            print('pred_tarid',pred_tarid)
            print('pred_tpfid',pred_tpfid_array)
            print('pred_tpsid',pred_tpsid_array)
            print('pred_tprid',pred_tprid)

        return [pred_tarid,
                pred_tasid_array,
                pred_tafid_array,
                pred_tprid,
                pred_tpsid_array,
                pred_tpfid_array]

    @property
    def chi2(self) : 
        
        debug = self.debug
        self.debug = True

        freeParams = self.freeParameterList() 
        p0 = []
        for p in freeParams : 
            p0.append(p.value)        
        chi2 = self.calculateChi2(p0)
        
        self.debug = debug
        return chi2
    
    @property 
    def numberFreeParameters(self) : 
        iFreeParams = 0
        freeParams = self.freeParameterList() 
        for p in freeParams : 
            iFreeParams = iFreeParams+1
        
        return iFreeParams

    def generateTALineup(self):
        memoryStrength = _np.random.normal(self.lureMean, self.targetMean, self.lineupSize)

        return [-1,memoryStrength]

    def generateTPLineup(self):
        memoryStrength   = _np.random.normal(self.lureMean, self.targetMean, self.lineupSize)
        lineupLocation = int(_math.floor(_np.random.rand()*self.lineupSize))
        targetStrength = _np.random.normal(self.targetMean,self.targetSigma,1)

        memoryStrength[lineupLocation] = targetStrength
        return [lineupLocation,memoryStrength]

    def generateFrequenciesForAllCriteria(self, mcScale = 20) :
        totalLineups = self.numberTALineups + self.numberTPLineups

        fractionTALineups = self.numberTALineups
        totalMCLineups    = mcScale*totalLineups

        pred_tafid_array = _np.zeros(self.numberConditions)
        pred_tpsid_array = _np.zeros(self.numberConditions)
        pred_tpfid_array = _np.zeros(self.numberConditions)

        for i in range(totalMCLineups) :
            r = _rand.random()
            if r < fractionTALineups :
                memoryStrength = self.generateTALineup()
            else :
                memoryStrength = self.generateTPLineup()


            self.monteCarloDecision(pred_tafid_array,
                                    pred_tpsid_array,
                                    pred_tpfid_array,
                                    memoryStrength)

        pred_tasid_array = pred_tafid_array / self.lineupSize
        pred_tarid = self.numberTALineups - pred_tafid_array.sum()
        pred_tprid = self.numberTPLineups - pred_tpsid_array.sum() - pred_tpfid_array.sum()

        return [pred_tarid,
                pred_tasid_array,
                pred_tafid_array,
                pred_tprid,
                pred_tpsid_array,
                pred_tpfid_array]

    def monteCarloDecision(self,pred_tafid_array, pred_tpsid_array, pred_tpfid_array, memoryStrength) :
        pass

    def calculateChi2(self, params) : 

        freeParams = self.freeParameterList()
        
        for i in range(0,len(freeParams),1) : 
            p = freeParams[i]
            p.value = params[i]
        
        if self.debug :
            print('iteration',self.iteration)
            print('params',params)

        [pred_tarid, pred_tasid_array, pred_tafid_array, 
         pred_tprid, pred_tpsid_array, pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        chi2_tafid = 0 
        chi2_tpsid = 0
        chi2_tpfid = 0
        chi2_tarid = 0
        chi2_tprid = 0
        for i in range(0,self.numberConditions) :
            chi2_tafid = chi2_tafid + (self.processedData.data_pivot.loc['targetAbsent' ,'fillerId'][i]  - pred_tafid_array[i])**2 / abs(pred_tafid_array[i]) # No for showups (TODO)
            chi2_tpsid = chi2_tpsid + (self.processedData.data_pivot.loc['targetPresent','suspectId'][i] - pred_tpsid_array[i])**2 / abs(pred_tpsid_array[i])
            chi2_tpfid = chi2_tpfid + (self.processedData.data_pivot.loc['targetPresent','fillerId'][i]  - pred_tpfid_array[i])**2 / abs(pred_tpfid_array[i]) # No for showups (TODO)

        chi2_tarid = (self.processedData.data_pivot.loc['targetAbsent' ,'rejectId'].sum() - pred_tarid)**2 / pred_tarid
        chi2_tprid = (self.processedData.data_pivot.loc['targetPresent','rejectId'].sum() - pred_tprid)**2 / pred_tprid

        chi2 = chi2_tafid + chi2_tpsid + chi2_tpfid + chi2_tarid + chi2_tprid

        if self.debug : 
            print('chi2 total', chi2)
            print('chi2 tafid', chi2_tafid)
            print('chi2 tarid', chi2_tarid)
            print('chi2 tpfid', chi2_tpfid)
            print('chi2 tpsid', chi2_tpsid)
            print('chi2 tprid', chi2_tprid)
        
        self.iteration = self.iteration+1
        return chi2        
            
    def fit(self, resetParameters = False) :

        if resetParameters :
            self.resetParameters()

        freeParams = self.freeParameterList()
        p0 = []
        for p in freeParams : 
            p0.append(p.value)

        if self.debug :
            print('fit> starting parameters',p0)

        self.iteration = 0

        def chiSquared(x) : 
            return self.calculateChi2(x)


        opt = _optimize.minimize(chiSquared,p0, method='Nelder-Mead')

        print(opt)

        # self.thresholds = opt['x'][0:self.numberConditions]

    def calculateConfidenceBootstrap(self, nBootstraps = 200) :
        self.debug = False

        chi2 = []
        c1   = []

        for i in range(0,nBootstraps,1) :
            dr = self.processedData.dataRaw.resampleWithReplacement()
            dp = dr.process()
            self.processedData = dp
            self.resetParameters()
            self.targetBetweenSigma.value = 0.3

            self.numberConditions = dp.numberConditions
            self.lineupSize       = dp.lineupSize
            self.numberTPLineups  = dp.numberTPLineups
            self.numberTALineups  = dp.numberTALineups
            self.pred_rates       = dp.data_rates.copy()  # copy the processed data rates for a prediction data frame
            self.pred_rates.iloc[:, :] = 0.0
            self.iteration = 0

            self.fit()
            self.printParameters()

            chi2.append(self.chi2)
            c1.append(self.c1.value)

        return [chi2,c1]

    def plotModel(self, xlow = -5, xhigh = 5) : 
        x      = _np.linspace(xlow, xhigh,200) 
        lure   = _norm.pdf(x,self.lureMean.value, self.lureSigma.value)
        target = _norm.pdf(x,self.targetMean.value, self.targetSigma.value)
        
        _plt.plot(x,lure)
        _plt.plot(x,target)
        for t in self.thresholds : 
            _plt.axvline(t.value, linestyle='--')

        _plt.xlabel("Memory strength")
        _plt.ylabel("Probability")

        # Tight layout for plot
        _plt.tight_layout()

    def plotFit(self) : 

        [pred_tarid,
         pred_tasid_array, 
         pred_tafid_array,
         pred_tprid, 
         pred_tpsid_array,
         pred_tpfid_array] = self.calculateFrequenciesForAllCriteria()

        x = range(0,pred_tasid_array.size,1)
    
        fig = _plt.figure(constrained_layout=True)
        gs = fig.add_gridspec(3,3)
        ax1 = fig.add_subplot(gs[0, 0:2])
        ax2 = fig.add_subplot(gs[1, 0:2])
        ax3 = fig.add_subplot(gs[2, 0:2])
                                    
        ax4 = fig.add_subplot(gs[0,2])
        ax5 = fig.add_subplot(gs[2,2])

        # tafid fit bar
        _plt.sca(ax1)
        _plt.bar(x,pred_tafid_array, fill=False)
        _plt.errorbar(x,
                      self.processedData.data_pivot.loc['targetAbsent' ,'fillerId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetAbsent' ,'fillerId']),
                      fmt='o',
                      markersize=5,
                      capsize=5) 
        _plt.ylabel("TA Filler ID")

        # tasid data plot
        _plt.sca(ax2)
        _plt.bar(x,pred_tpsid_array, fill=False)
        _plt.errorbar(x,
                      self.processedData.data_pivot.loc['targetPresent' ,'suspectId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent' ,'suspectId']),
                      fmt='o',
                      markersize=5,
                      capsize=5) 
        _plt.ylabel("TP Suspect ID")

        # tpfid data plot
        _plt.sca(ax3) 
        _plt.bar(x,pred_tpfid_array, fill=False)
        _plt.errorbar(x,
                      self.processedData.data_pivot.loc['targetPresent' ,'fillerId'],
                      _np.sqrt(self.processedData.data_pivot.loc['targetPresent' ,'fillerId']),
                      fmt='o',
                      markersize=5,
                      capsize=5)  
        _plt.ylabel("TP Filler ID")

        # tarid data plot
        _plt.sca(ax4)
        _plt.bar([0],[pred_tarid],fill=False)
        _plt.errorbar([0],
                      [self.processedData.data_pivot.loc['targetAbsent' ,'rejectId'].sum()],
                      [_np.sqrt(self.processedData.data_pivot.loc['targetAbsent' ,'rejectId'].sum())],
                      fmt='o',
                      markersize=5,
                      capsize=5)  
        _plt.ylabel("TA Reject ID")

        # tarid data plot
        _plt.sca(ax5)
        _plt.bar([0],[pred_tprid],fill=False)
        _plt.errorbar([0],
                      [self.processedData.data_pivot.loc['targetPresent' ,'rejectId'].sum()],
                      [_np.sqrt(self.processedData.data_pivot.loc['targetPresent' ,'rejectId'].sum())],
                      fmt='o',
                      markersize=5,
                      capsize=5)  
        _plt.ylabel("TP Reject ID")
            
    def plotROC(self, criterion1 = 0, criterion2 = 5, nsteps = 50, label = "Indep model" ) :
        
        rate_tafid_array = []
        rate_tpfid_array = []
        rate_tpsid_array = []
        
        for x in _np.linspace(criterion1,criterion2,nsteps) : 
            [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateCumulativeFrequencyForCriterion(x)
                       
            rate_tafid_array.append(pred_tafid/self.lineupSize/self.numberTALineups)
            rate_tpfid_array.append(pred_tpfid/self.numberTPLineups)
            rate_tpsid_array.append(pred_tpsid/self.numberTPLineups)
            
        _plt.plot(rate_tafid_array,rate_tpsid_array, linestyle = '--', label=label)
            
    def plotCAC(self, nsteps = 50, label = "Indep model") :
        
        # need to create look up between confidence and criterion
        confidence = self.processedData.data_rates.columns.get_level_values('confidence')
        criterion  = self.thresholds[-1::-1]

        print(confidence)
        print(criterion)

        confidenceMin = confidence.min()
        confidenceMax = confidence.max()

        confCriterionInterpol = _interpolate.interp1d(confidence, criterion)
        
        confidence_array = []

        rate_tafid_array = []
        rate_tasid_array = []
        rate_tpfid_array = []
        rate_tpsid_array = []
        
        for x in _np.linspace(confidenceMin,confidenceMax,nsteps) : 
            [pred_tafid, pred_tpsid, pred_tpfid] = self.calculateFrequencyForCriterion(confCriterionInterpol(x))
        
            confidence_array.append(x)
            rate_tafid_array.append(pred_tafid/self.numberTALineups)
            rate_tasid_array.append(pred_tafid/self.lineupSize/self.numberTALineups)
            rate_tpfid_array.append(pred_tpfid/self.numberTPLineups)
            rate_tpsid_array.append(pred_tpsid/self.numberTPLineups)
            
        confidence_array = _np.array(confidence_array)
        rate_tafid_array = _np.array(rate_tafid_array)
        rate_tasid_array = _np.array(rate_tasid_array)
        rate_tpfid_array = _np.array(rate_tpfid_array)
        rate_tpsid_array = _np.array(rate_tpsid_array)

        cac = rate_tpsid_array/(rate_tpsid_array+rate_tafid_array)
        
        _plt.plot(confidence_array, cac, linestyle = '--', label=label)

###########################################################################################################################################
class ModelFitIndependentObservationSimple(ModelFit) :
    def __init__(self, processedData, debug = False, integrationSigma = 8) :
        ModelFit.__init__(self,processedData, debug = debug, integrationSigma = integrationSigma)
        
    def calculateCumulativeFrequencyForCriterion(self, c) :
        # target ID in target present lineups 
        def probTargetIDTargetPresent(x) :
            return _norm.cdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1)*_norm.pdf(x,self.targetMean.value, self.targetSigma.value)
        
        def probTargetIDTargetPresentIntegral(x1, x2) :
            return _integrate.quad(probTargetIDTargetPresent,x1,x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x) : 
            return _norm.cdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-2)*_norm.pdf(x,self.lureMean.value, self.lureSigma.value)*_norm.cdf(x,self.targetMean.value, self.targetSigma.value)

        def probFillerIDTargetPresentIntegral(x1, x2) :
           return _integrate.quad(probFillerIDTargetPresent,x1,x2)[0]

        # filler ID (suspect ID) in target absent lineups 
        def probFillerIDTargetAbsentIntegral(x1) :
            return _norm.cdf(x1)**self.lineupSize

        prob_tpsid = probTargetIDTargetPresentIntegral(float(c),6)
        prob_tpfid = (self.lineupSize-1)*probFillerIDTargetPresentIntegral(float(c),6)
        prob_tafid = 1-probFillerIDTargetAbsentIntegral(float(c))

        pred_tpsid = prob_tpsid*self.numberTPLineups
        pred_tpfid = prob_tpfid*self.numberTPLineups
        pred_tafid = prob_tafid*self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])

###########################################################################################################################################
class ModelFitIndependentObservation(ModelFit) :
    def __init__(self, processedData, debug = False, integrationSigma = 8) :
        ModelFit.__init__(self,processedData, debug = debug, integrationSigma = integrationSigma)

    def setEqualVariance(self) :
        super().setEqualVariance()

        self.targetBetweenSigma.fixed = False
        self.targetBetweenSigma.value = 0.3

    def monteCarloDecision(self,pred_tafid_array, pred_tpsid_array, pred_tpfid_array, memoryStrength) :
        pass

    def calculateCumulativeFrequencyForCriterion(self, c) :

        self.calculateWithinSigmas()

        # target ID in target present lineups 

        def probTargetIDTargetPresent(x) :
            return normcdf(x,self.lureMean.value, self.lureWithinSigma)**(self.lineupSize-1)*\
                   normpdf(x,self.targetMean.value, self.targetWithinSigma)*\
                   (1-normcdf(float(c),x,self.targetBetweenSigma.value))

        def probTargetIDTargetPresentIntegral(x1, x2) :
            return _integrate.quad(probTargetIDTargetPresent,x1,x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x) : 
            return normcdf(x,self.lureMean.value, self.lureWithinSigma)**(self.lineupSize-2)*\
                   normpdf(x,self.lureMean.value, self.lureWithinSigma)*\
                   normcdf(x,self.targetMean.value, self.targetWithinSigma)*\
                   (1-normcdf(float(c),x,self.targetBetweenSigma.value))

        def probFillerIDTargetPresentIntegral(x1, x2) :
            return _integrate.quad(probFillerIDTargetPresent,x1,x2)[0]

        def probFillerIDTargetAbsent(x) :
            return normpdf(x,self.lureMean.value,self.lureWithinSigma)*\
                   normcdf(x,self.lureMean.value, self.lureWithinSigma)**(self.lineupSize-1)*\
                   (1-normcdf(float(c),x,self.targetBetweenSigma.value))

        # filler ID (suspect ID) in target absent lineups 
        def probFillerIDTargetAbsentIntegral(x1,x2) :
           return _integrate.quad(probFillerIDTargetAbsent,x1,x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(self.targetMean.value - self.targetSigma.value * self.integrationSigma ,
                                                       self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize-1)*probFillerIDTargetPresentIntegral(self.lureMean.value - self.lureSigma.value * self.integrationSigma ,
                                                                           self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize*probFillerIDTargetAbsentIntegral(self.lureMean.value - self.lureSigma.value * self.integrationSigma ,
                                                                      self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid*self.numberTPLineups
        pred_tpfid = prob_tpfid*self.numberTPLineups
        pred_tafid = prob_tafid*self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])

###########################################################################################################################################
class ModelFitBestRest(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma)

    def mean(self, w, lm, ls, tm, ts, nlineup):
        tlm = truncatedMean(lm, ls, w)
        ttm = truncatedMean(tm, ts, w)

        return w - ( (nlineup-2)*tlm + ttm )/(nlineup-1)

    def sigma(self, w, lm, ls, tm, ts, nlineup):
        tlv = truncatedVar(lm, ls, w)
        ttv = truncatedVar(tm, ts, w)

        return _np.sqrt( ((nlineup-2)*tlv + ttv) / (nlineup-1)**2 )

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        # target ID in target present lineups
        def probTargetIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                   normpdf(x, self.targetMean.value, self.targetSigma.value) * \
                   (1 - normcdf(float(c),
                                self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                          self.lureSigma.value, self.lineupSize),
                                self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                           self.lureSigma.value, self.lineupSize)
                                )
                    )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetPresent(x):
            return normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 2) * \
                   normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                   normcdf(x, self.targetMean.value, self.targetSigma.value) * \
                   (1 - normcdf(float(c),
                                self.mean(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                          self.targetSigma.value, self.lineupSize),
                                self.sigma(x, self.lureMean.value, self.lureSigma.value, self.targetMean.value,
                                           self.targetSigma.value, self.lineupSize)
                                )
                    )

        # filler ID in target present lineups
        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetAbsent(x):
            return normpdf(x, self.lureMean.value, self.lureSigma.value) * \
                   normcdf(x, self.lureMean.value, self.lureSigma.value) ** (self.lineupSize - 1) * \
                   (1 - normcdf(float(c),
                                self.mean(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                          self.lureSigma.value, self.lineupSize),
                                self.sigma(x, self.lureMean.value, self.lureSigma.value, self.lureMean.value,
                                           self.lureSigma.value, self.lineupSize))
                    )

            # filler ID (suspect ID) in target absent lineups
        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(
            self.targetMean.value - self.targetSigma.value * self.integrationSigma,
            self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(
            self.lureMean.value - self.lureSigma.value * self.integrationSigma,
            self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])

###########################################################################################################################################
class ModelFitEnsemble(ModelFit) :
    def __init__(self, processedData, debug = False, integrationSigma = 8) :
        ModelFit.__init__(self,processedData, debug = debug, integrationSigma = integrationSigma)

    def mean(self,w, lm, ls, tm, ts, nlineup) :
        tlm = truncatedMean(lm,ls,w)
        ttm = truncatedMean(tm,ts,w)

        return (w*(nlineup-1)-tlm*(nlineup-2)-ttm)/nlineup

    def sigma(self,w, lm, ls, tm, ts, nlineup) :
        tlv = truncatedVar(lm,ls,w)
        ttv = truncatedVar(tm,ts,w)

        return _np.sqrt((ttv+(nlineup-2)*tlv)/nlineup**2)

    def calculateCumulativeFrequencyForCriterion(self, c) :

        self.calculateWithinSigmas()

        # target ID in target present lineups
        def probTargetIDTargetPresent(x) :
            return normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1)*\
                   normpdf(x,self.targetMean.value, self.targetSigma.value)*\
                   (1-normcdf(float(c),
                              self.mean( x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize),
                              self.sigma(x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize)
                              )
                    )

        def probTargetIDTargetPresentIntegral(x1, x2) :
            return _integrate.quad(probTargetIDTargetPresent,x1,x2)[0]

        def probFillerIDTargetPresent(x) :
            return normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-2)*\
                   normpdf(x,self.lureMean.value, self.lureSigma.value)*\
                   normcdf(x,self.targetMean.value, self.targetSigma.value)*\
                   (1-normcdf(float(c),
                              self.mean( x,self.lureMean.value, self.lureSigma.value,self.targetMean.value,self.targetSigma.value,self.lineupSize),
                              self.sigma(x,self.lureMean.value, self.lureSigma.value,self.targetMean.value,self.targetSigma.value,self.lineupSize)
                              )
                    )
        # filler ID in target present lineups
        def probFillerIDTargetPresentIntegral(x1, x2) :
           return _integrate.quad(probFillerIDTargetPresent,x1,x2)[0]

        def probFillerIDTargetAbsent(x) :
            return normpdf(x,self.lureMean.value,self.lureSigma.value)*\
                   normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1)*\
                   (1-normcdf(float(c),
                              self.mean( x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize),
                              self.sigma(x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize)                              )
                    )

        # filler ID (suspect ID) in target absent lineups
        def probFillerIDTargetAbsentIntegral(x1,x2) :
           return _integrate.quad(probFillerIDTargetAbsent,x1,x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(self.targetMean.value - self.targetSigma.value * self.integrationSigma ,
                                                       self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize-1)*probFillerIDTargetPresentIntegral(self.lureMean.value - self.lureSigma.value * self.integrationSigma ,
                                                                           self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize*probFillerIDTargetAbsentIntegral(self.lureMean.value - self.lureSigma.value * self.integrationSigma ,
                                                                      self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid*self.numberTPLineups
        pred_tpfid = prob_tpfid*self.numberTPLineups
        pred_tafid = prob_tafid*self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])

###########################################################################################################################################
class ModelFitIntegration(ModelFit):
    def __init__(self, processedData, debug=False, integrationSigma=8):
        ModelFit.__init__(self, processedData, debug=debug, integrationSigma=integrationSigma)

    def mean(self,w, lm, ls, tm, ts, nlineup) :
        tlm = truncatedMean(lm,ls,w)
        ttm = truncatedMean(tm,ts,w)

        return w + ttm + (nlineup-2)*tlm

    def sigma(self,w, lm, ls, tm, ts, nlineup) :
        tlv = truncatedVar(lm,ls,w)
        ttv = truncatedVar(tm,ts,w)

        return _np.sqrt(nlineup**2*self.targetBetweenSigma.value**2 + ttv + (nlineup-2)*tlv)

    def calculateCumulativeFrequencyForCriterion(self, c):
        self.calculateWithinSigmas()

        # target ID in target present lineups
        def probTargetIDTargetPresent(x):
            return normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1)*\
                   normpdf(x,self.targetMean.value, self.targetSigma.value)*\
                   (1-normcdf(float(c),
                              self.mean( x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize),
                              self.sigma(x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize)
                              )
                    )

        def probTargetIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

        # filler ID in target present lineups
        def probFillerIDTargetPresent(x):
            return normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-2)*\
                   normpdf(x,self.lureMean.value, self.lureSigma.value)*\
                   normcdf(x,self.targetMean.value, self.targetSigma.value)*\
                   (1-normcdf(float(c),
                              self.mean( x,self.lureMean.value, self.lureSigma.value,self.targetMean.value,self.targetSigma.value,self.lineupSize),
                              self.sigma(x,self.lureMean.value, self.lureSigma.value,self.targetMean.value,self.targetSigma.value,self.lineupSize)
                              )
                    )

        def probFillerIDTargetPresentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

        def probFillerIDTargetAbsent(x):
            return normpdf(x,self.lureMean.value,self.lureSigma.value)*\
                   normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1)*\
                   (1-normcdf(float(c),
                              self.mean( x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize),
                              self.sigma(x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize)                              )
                    )

        # filler ID (suspect ID) in target absent lineups
        def probFillerIDTargetAbsentIntegral(x1, x2):
            return _integrate.quad(probFillerIDTargetAbsent, x1, x2)[0]

        prob_tpsid = probTargetIDTargetPresentIntegral(self.targetMean.value - self.targetSigma.value * self.integrationSigma,
                                                       self.targetMean.value + self.targetSigma.value * self.integrationSigma)
        prob_tpfid = (self.lineupSize - 1) * probFillerIDTargetPresentIntegral(self.lureMean.value - self.lureSigma.value * self.integrationSigma,
                                                                               self.lureMean.value + self.lureSigma.value * self.integrationSigma)
        prob_tafid = self.lineupSize * probFillerIDTargetAbsentIntegral(self.lureMean.value - self.lureSigma.value * self.integrationSigma,
                                                                        self.lureMean.value + self.lureSigma.value * self.integrationSigma)

        pred_tpsid = prob_tpsid * self.numberTPLineups
        pred_tpfid = prob_tpfid * self.numberTPLineups
        pred_tafid = prob_tafid * self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])