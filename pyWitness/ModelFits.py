import numpy as _np
from scipy import integrate as _integrate
from scipy import optimize as _optimize
from scipy import interpolate as _interpolate
from scipy.stats import norm as _norm
import matplotlib.pyplot as _plt

class ModelFit :
    def __init__(self, processedData) : 
        self.processedData    = processedData 
        self.numberConditions = processedData.numberConditions
        self.lineupSize       = processedData.lineupSize
        self.numberTPLineups  = processedData.numberTPLineups
        self.numberTALineups  = processedData.numberTALineups
        self.pred_rates       = processedData.data_rates.copy()           # copy the processed data rates for a prediction data frame
        self.pred_rates.iloc[:,:] = 0.0
        self.iteration        = 0
        self.debug            = False

        # parameters 
        self.lureMean         = 0.0
        self.lureSigma        = 1.0
        self.targetMean       = 1.0
        self.targetSigma      = 1.0
        self.thresholds  = _np.linspace(self.targetMean, self.targetMean+self.targetSigma, self.numberConditions) # linearly spread the initial thresholds 

    def calculateFrequencyForCriterion(self, c1, c2) :
        pred_c1 = self.calculateCumulativeFrequencyForCriterion(c1)
        pred_c2 = self.calculateCumulativeFrequencyForCriterion(c2)

        return pred_c2 - pred_c1
    
    def calculateFrequenciesForAllCriteria(self) : 
        
        pred_tafid_array = []
        pred_tpsid_array = []
        pred_tpfid_array = []
   
        for i in range(0,self.thresholds.size,1) : 
            if i < self.thresholds.size-1 : 
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
    
    def calculateChi2(self, params) : 

        params = _np.array(params)

        self.thresholds  = params[0:self.numberConditions]
        # self.lureSigma   = params[self.numberConditions]
        self.targetMean  = params[self.numberConditions+0]
        self.targetSigma = params[self.numberConditions+1]
        
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
            chi2_tafid = chi2_tafid + (self.processedData.data_pivot.loc['targetAbsent' ,'fillerId'][i]  - pred_tafid_array[i])**2 / pred_tafid_array[i]
            chi2_tpsid = chi2_tpsid + (self.processedData.data_pivot.loc['targetPresent','suspectId'][i] - pred_tpsid_array[i])**2 / pred_tpsid_array[i]
            chi2_tpfid = chi2_tpfid + (self.processedData.data_pivot.loc['targetPresent','fillerId'][i]  - pred_tpfid_array[i])**2 / pred_tpfid_array[i] # No for showups (TODO)

        chi2_tarid = (self.processedData.data_pivot.loc['targetAbsent' ,'rejectId'].sum() - pred_tarid)**2 / pred_tarid
        chi2_tprid = (self.processedData.data_pivot.loc['targetPresent','rejectId'].sum() - pred_tprid)**2 / pred_tprid

        chi2 = chi2_tafid + chi2_tpsid + chi2_tpfid + chi2_tarid + chi2_tprid

        print('chi2 total', chi2)
        print('chi2 tafid', chi2_tafid)
        print('chi2 tarid', chi2_tarid)
        print('chi2 tpfid', chi2_tpfid)
        print('chi2 tpsid', chi2_tpsid)
        print('chi2 tprid', chi2_tprid)
        
        self.iteration = self.iteration+1
        return chi2        
            
    def fit(self) : 
        x0 = [1.52501177, 1.94621728, 2.52453685, 1.77685984, 0.76298395]
        
        self.iteration = 0

        def chiSquared(x) : 
            return self.calculateChi2(x)

        opt = _optimize.minimize(chiSquared, x0, method='Nelder-Mead')
        print(opt)
        self.thresholds = opt['x'][0:self.numberConditions]
        
    def plotModel(self, xlow = -5, xhigh = 5) : 
        x      = _np.linspace(xlow, xhigh,200) 
        lure   = _norm.pdf(x,self.lureMean, self.lureSigma)
        target = _norm.pdf(x,self.targetMean, self.targetSigma)
        
        _plt.plot(x,lure)
        _plt.plot(x,target)
        for t in self.thresholds : 
            _plt.axvline(t, linestyle='--')

        _plt.xlabel("Memory strength")
        _plt.ylabel("Probability")

        # Tight layout for plot
        _plt.tight_layout()

    def plotFit(self) : 
        pass

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

class ModelFitIndependentObservation :
    def __init__(self, processedData) : 
        self.processedData    = processedData 
        self.numberConditions = processedData.numberConditions
        self.lineupSize       = processedData.lineupSize
        self.numberTPLineups  = processedData.numberTPLineups
        self.numberTALineups  = processedData.numberTALineups
        self.pred_rates       = processedData.data_rates.copy()           # copy the processed data rates for a prediction data frame
        self.pred_rates.iloc[:,:] = 0.0
        self.iteration        = 0
        self.debug            = False

        # parameters 
        self.lureMean    = 0.0
        self.lureSigma   = 1.0
        self.targetMean  = 1.0
        self.targetSigma = 1.0
        self.thresholds  = _np.linspace(self.targetMean, self.targetMean+self.targetSigma, self.numberConditions) # linearly spread the initial thresholds 

    def setParameters(self) : 
        pass

    def calculateCumulativeFrequencyForCriterion(self, c) :
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

        prob_tpsid = probTargetIDTargetPresentIntegral(c,6)
        prob_tpfid = (self.lineupSize-1)*probFillerIDTargetPresentIntegral(c,6)
        prob_tafid = 1-probFillerIDTargetAbsentIntegral(c)

        pred_tpsid = prob_tpsid*self.numberTPLineups
        pred_tpfid = prob_tpfid*self.numberTPLineups
        pred_tafid = prob_tafid*self.numberTALineups

        return _np.array([pred_tafid, pred_tpsid, pred_tpfid])

    def calculateFrequencyForCriterion(self, c1, c2) :
        pred_c1 = self.calculateCumulativeFrequencyForCriterion(c1)
        pred_c2 = self.calculateCumulativeFrequencyForCriterion(c2)

        return pred_c2 - pred_c1
    
    def calculateFrequenciesForAllCriteria(self) : 
        
        pred_tafid_array = []
        pred_tpsid_array = []
        pred_tpfid_array = []
   
        for i in range(0,self.thresholds.size,1) : 
            if i < self.thresholds.size-1 : 
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
    
    def calculateChi2(self, params) : 

        params = _np.array(params)

        self.thresholds  = params[0:self.numberConditions]
        # self.lureSigma   = params[self.numberConditions]
        self.targetMean  = params[self.numberConditions+0]
        self.targetSigma = params[self.numberConditions+1]
        
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
            chi2_tafid = chi2_tafid + (self.processedData.data_pivot.loc['targetAbsent' ,'fillerId'][i]  - pred_tafid_array[i])**2 / pred_tafid_array[i]
            chi2_tpsid = chi2_tpsid + (self.processedData.data_pivot.loc['targetPresent','suspectId'][i] - pred_tpsid_array[i])**2 / pred_tpsid_array[i]
            chi2_tpfid = chi2_tpfid + (self.processedData.data_pivot.loc['targetPresent','fillerId'][i]  - pred_tpfid_array[i])**2 / pred_tpfid_array[i] # No for showups (TODO)

        chi2_tarid = (self.processedData.data_pivot.loc['targetAbsent' ,'rejectId'].sum() - pred_tarid)**2 / pred_tarid
        chi2_tprid = (self.processedData.data_pivot.loc['targetPresent','rejectId'].sum() - pred_tprid)**2 / pred_tprid

        chi2 = chi2_tafid + chi2_tpsid + chi2_tpfid + chi2_tarid + chi2_tprid

        print('chi2 total', chi2)
        print('chi2 tafid', chi2_tafid)
        print('chi2 tarid', chi2_tarid)
        print('chi2 tpfid', chi2_tpfid)
        print('chi2 tpsid', chi2_tpsid)
        print('chi2 tprid', chi2_tprid)
        
        self.iteration = self.iteration+1
        return chi2        
            
    def fit(self) : 
        x0 = [1.52501177, 1.94621728, 2.52453685, 1.77685984, 0.76298395]
        
        self.iteration = 0

        def chiSquared(x) : 
            return self.calculateChi2(x)

        opt = _optimize.minimize(chiSquared, x0, method='Nelder-Mead')
        print(opt)
        self.thresholds = opt['x'][0:self.numberConditions]
        
    def plotModel(self, xlow = -5, xhigh = 5) : 
        x      = _np.linspace(xlow, xhigh,200) 
        lure   = _norm.pdf(x,self.lureMean, self.lureSigma)
        target = _norm.pdf(x,self.targetMean, self.targetSigma)
        
        _plt.plot(x,lure)
        _plt.plot(x,target)
        for t in self.thresholds : 
            _plt.axvline(t, linestyle='--')

        _plt.xlabel("Memory strength")
        _plt.ylabel("Probability")

        # Tight layout for plot
        _plt.tight_layout()

    def plotFit(self) : 
        pass

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

