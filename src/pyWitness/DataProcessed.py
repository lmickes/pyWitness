import pandas as _pandas
import matplotlib.pyplot as _plt
import numpy as _np
import math as _math
import scipy.integrate as _integrate
import scipy.special as _special
import scipy.optimize as _optimize
import copy as _copy

bPAUCNanWarning = True

class DataProcessed :
    '''
    Processed data class 
    
    :param dataRaw: Instance of raw data class or csv file name with binned data
    :type dataRaw: str or DataRaw
    :param reverseConfidence: Flag if confidence decreases with increasing numerical value
    :type reverseConfidence: bool
    :param lineupSize: Number of people in the lineup
    :type lineupSize: int 
    
    '''
    
    def __init__(self, dataRaw, reverseConfidence = False, lineupSize = 1, pAUCLiberal = 1.0, levels = None, option="all", dependentVariable = "confidence", baseRate = 0.5) :

        self.debugIoPadSize = 35

        if isinstance(dataRaw, str) :
            # could just load the data frame from csv, but want to have in exactly same format. 

            data_pivot_load = _pandas.read_csv(dataRaw)

            nrows = data_pivot_load.shape[0]
            
            # columns 
            columns = data_pivot_load.columns.values[1:]

            # loop over rows
            for i in range(0,nrows,1) : 
                rowLabel = data_pivot_load.iloc[i].values[0]
                rowData  = data_pivot_load.iloc[i].values[1:] 

            data_pivot_load = data_pivot_load.drop("confidence",axis=1)
            cols = _pandas.MultiIndex.from_product([["confidence"], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],names=[None,"confidence"])
            inds = _pandas.MultiIndex.from_product([["targetAbsent","targetPresent"],["fillerId","rejectId","suspectId"]],names=['targetLineup', 'responseType'])
            inds = inds.drop(('targetAbsent','suspectId'))

            data_pivot_load.columns = cols
            data_pivot_load.index   = inds

            self.data_pivot = data_pivot_load

            self.lineupSize        = lineupSize
            self.dataRaw           = None
            self.dependentVariable = dependentVariable
            self.reverseConfidence = reverseConfidence
        else :
            self.dataRaw           = dataRaw
            self.lineupSize        = lineupSize 
            self.reverseConfidence = reverseConfidence
            self.dependentVariable = self.dataRaw.dependentVariable
            self.calculatePivot()

            if levels is not None :
                self.data_pivot = self.data_pivot.reindex(columns=levels, fill_value=0)
            self.confidenceLevels =  self.data_pivot.columns # _np.sort(self.dataRaw.data['confidence'].unique())

        self.numberTPLineups   = self.data_pivot.loc['targetPresent'].sum().sum()
        self.numberTALineups   = self.data_pivot.loc['targetAbsent'].sum().sum()

        self.pAUCLiberal = pAUCLiberal
        self.baseRate = baseRate

        self.calculateRates()
        self.calculateDPrime()
        self.calculateCriterion()
        self.calculateConfidence()
        if option == "all" :
            self.calculateRelativeFrequency()
            self.calculateCAC()
            self.calculateCARC()
            self.calculatePAUC(pAUCLiberal)
            self.calculateNormalisedAUC()
            

        self.bootstrapped = False

        if self.reverseConfidence :
            self.data_rates.loc[self.dependentVariable,'central'] = list(self.data_rates.loc[self.dependentVariable,'central'][::-1])

    def calculatePivot(self) : 
        ''' 
        Calculate fequency pivot table against 'confidence'

        :rtype: None
        '''
        
        self.data_pivot = _pandas.pivot_table(self.dataRaw.dataSelected, 
                                              columns=self.dependentVariable,
                                              index=['targetLineup','responseType'], 
                                              aggfunc={self.dependentVariable:'count'})

        # reverse confidence
        if self.reverseConfidence :
            columns = self.data_pivot.columns.tolist()
            columns = columns[::-1]
            self.data_pivot = self.data_pivot[columns]

        # TODO understand why this is needed. At appears targetAbsent lineup suspectId appears even if 0 in pivot
        try :
            if self.data_pivot.loc['targetAbsent','suspectId'].sum() == 0 :
                self.data_pivot.drop(index=('targetAbsent','suspectId'), inplace=True)
        except :
            pass

        # TODO understand NA removal
        self.data_pivot.fillna(0,inplace=True)

        # If showup fold the rejectID into the suspectID rates
        if self.lineupSize == 1 :
            pass

    def calculateRates(self) :
        ''' 
        Calculate cumulative rates from data_pivot. Result stored in data_rates

        :rtype: None
        '''
        
        self.data_rates = self.data_pivot.copy()

        # rename multiindex
        self.data_rates.index.names = ["variable", "type"]

        # reverse confidence
        self.data_rates = self.data_rates.reindex(columns=self.data_rates.columns[::-1])

        # cumulative rates
        self.data_rates = self.data_rates.cumsum(1)

        self.targetAbsentSum   = self.data_pivot.loc['targetAbsent'].sum().sum()
        self.targetPresentSum  = self.data_pivot.loc['targetPresent'].sum().sum()
        
        try :
            self.data_rates.loc['targetAbsent','fillerId']  = self.data_rates.loc['targetAbsent','fillerId']/self.targetAbsentSum          
        except KeyError :
            pass

        try :
            self.data_rates.loc['targetAbsent','designateId']  = self.data_rates.loc['targetAbsent','designateId']/self.targetAbsentSum
        except KeyError :
            pass

        try :
            if self.lineupSize != 1 :
                self.data_rates.loc['targetAbsent','suspectId'] = self.data_rates.loc['targetAbsent','suspectId']/self.targetAbsentSum
            else :
                self.data_rates.loc['targetAbsent','suspectId'] = (self.data_rates.loc['targetAbsent','rejectId'] + self.data_rates.loc['targetAbsent','suspectId'])  /self.targetAbsentSum
        except KeyError :
            pass

        try :
            self.data_rates.loc['targetAbsent','rejectId']  = self.data_rates.loc['targetAbsent','rejectId']/self.targetAbsentSum
        except KeyError :
            pass

        try :
            self.data_rates.loc['targetPresent','fillerId']  = self.data_rates.loc['targetPresent','fillerId']/self.targetPresentSum
        except KeyError :
            pass

        try :
            if self.lineupSize != 1:
                self.data_rates.loc['targetPresent','suspectId'] = self.data_rates.loc['targetPresent','suspectId']/self.targetPresentSum
            else :
                self.data_rates.loc['targetPresent','suspectId'] = (self.data_rates.loc['targetPresent','rejectId'] + self.data_rates.loc['targetPresent','suspectId']) /self.targetPresentSum
        except KeyError :
            pass

        try :
            self.data_rates.loc['targetPresent','rejectId']  = self.data_rates.loc['targetPresent','rejectId']/self.targetPresentSum
        except KeyError :
            pass


        # check if there is a suspect id in targetAbsent lineups (if not estimate) 
        try : 
            self.data_rates.loc['targetAbsent','suspectId']
        except :
            if self.lineupSize != 1 and not self.isDesignateId():  # Only estimate if this is a lineup (fillers dont exist for showups)
                suspectId = self.data_rates.loc['targetAbsent','fillerId']/self.lineupSize
                suspectId.name = ("targetAbsent","suspectId")
                self.data_rates = _pandas.concat([self.data_rates,_pandas.DataFrame(suspectId).transpose()])
                self.data_rates = self.data_rates.sort_index()
            elif self.lineupSize != 1 and self.isDesignateId():
                suspectId = self.data_rates.loc['targetAbsent','designateId']
                suspectId.name = ("targetAbsent","suspectId")
                self.data_rates = _pandas.concat([self.data_rates,_pandas.DataFrame(suspectId).transpose()])
                self.data_rates = self.data_rates.sort_index()

    def calculateConfidence(self):

        '''
        Calculate average confidence for a bin. Result stored in data_rates['confidence']
        '''

        confidence_mean = _copy.copy(self.data_rates.loc['targetPresent','suspectId'])

        if self.dataRaw is None :
            confidence_mean.name = (self.dependentVariable, "central")
        else :
            confidence_mean.name = (self.dependentVariable,"central")

        if self.dataRaw and self.dataRaw.collapseContinuous :
            for i in range(0,len(self.dataRaw.collapseContinuousLabels)) :
                label = self.dataRaw.collapseContinuousLabels[i]
                conf_label = self.dataRaw.data[self.dependentVariable+'_original'][self.dataRaw.data[self.dependentVariable] == label]
                conf_mean  = conf_label.mean()

                confidence_mean[len(self.dataRaw.collapseContinuousLabels)-i-1] = conf_mean

            self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(confidence_mean).transpose()])
            self.data_rates = self.data_rates.sort_index()
        else :
            confidence_mean = _copy.copy(self.data_rates.loc['targetPresent', 'suspectId'])
            confidence_mean.name = ("confidence", "central")

            if self.dataRaw is None :
                confidence = self.data_rates.columns.get_level_values(self.dependentVariable).values
            else :
                confidence = self.data_rates.columns.get_level_values(self.dependentVariable).values
            confidence_mean[:] = confidence

            self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(confidence_mean).transpose()])
            self.data_rates = self.data_rates.sort_index()

    def calculateRelativeFrequency(self) :

        '''
        Calculate relative frequency from data_pivot. Result stored in data_rates['cf']
        '''

        if self.lineupSize != 1 :                                                                           # SHOWUP
            cid = self.data_pivot.loc['targetPresent','suspectId']
        else :
            try : 
                cid = self.data_pivot.loc['targetPresent','suspectId'] + self.data_pivot.loc['targetPresent','rejectId']
            except :
                cid = self.data_pivot.loc['targetPresent','suspectId']
        try :
            if self.lineupSize != 1 :                                                                       # SHOWUP
                fid = self.data_pivot.loc['targetAbsent','suspectId']
            else :
                try :
                    fid = self.data_pivot.loc['targetAbsent','suspectId'] + self.data_pivot.loc['targetAbsent','rejectId']
                except :
                    fid = self.data_pivot.loc['targetAbsent','rejectId']

        except KeyError :            
            fid = self.data_pivot.loc['targetAbsent','fillerId']/self.lineupSize

        rf = (cid + fid)/(cid.sum() + fid.sum())
        rf.name = ("rf","") 
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(rf).transpose()])
        self.data_rates = self.data_rates.sort_index()

    def calculateRejectionRelativeFrequency(self,):
        '''
        Calculate relative frequency from data_pivot. Result stored in data_rates['rf_reject']
        '''
        if self.lineupSize != 1:                                                                           # LINEUP
            r_tp = self.data_pivot.loc['targetPresent','rejectId']
        else:
            try:
                r_tp = self.data_pivot.loc['targetPresent','rejectId'] + self.data_pivot.loc['targetPresent','suspectId']
            except:
                r_tp = self.data_pivot.loc['targetPresent','rejectId']

        try:
            if self.lineupSize != 1:                                                                        # LINEUP
                r_ta = self.data_pivot.loc['targetAbsent','suspectId']
            else:
                try:
                    r_ta = self.data_pivot.loc['targetAbsent','rejectId'] + self.data_pivot.loc['targetAbsent','suspectId']
                except:
                    r_ta = self.data_pivot.loc['targetAbsent','rejectId']

        except KeyError:
            r_ta = self.data_pivot.loc['targetAbsent','rejectId']

        rf_reject = (r_tp + r_ta) / (r_tp.sum() + r_ta.sum())
        rf_reject.name = ("rf_reject", "")
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(rf_reject).transpose()])
        self.data_rates = self.data_rates.sort_index()

    def calculateCAC(self) :
        '''
        Calculate confidence accuracy characteristic from data_pivot. Result stored in data_rates['cac']
        '''

        baseRate = self.baseRate

        if self.lineupSize != 1 :                                                                           # LINEUP
            cid = self.data_pivot.loc['targetPresent','suspectId']

            try:
                fid = self.data_pivot.loc['targetAbsent','designateId']
            except KeyError:
                fid = self.data_pivot.loc['targetAbsent', 'fillerId'] / self.lineupSize

            cac = baseRate * cid / (baseRate * cid + (1 - baseRate) * fid)

        else :                                                                                              # SHOWUP
            cid_baseRate_mod = self.data_pivot.loc['targetPresent', 'suspectId'] * baseRate + self.data_pivot.loc[
                'targetAbsent', 'rejectId'] * (1 - baseRate)
            fid_baseRate_mod = self.data_pivot.loc['targetPresent', 'rejectId'] * baseRate + self.data_pivot.loc[
                'targetAbsent', 'suspectId'] * (1 - baseRate)

            cac = cid_baseRate_mod / (cid_baseRate_mod + fid_baseRate_mod)

        cac.name = ("cac","central")
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(cac).transpose()])
        self.data_rates = self.data_rates.sort_index()

    def calculateCARC(self):
        '''
        Calculate Confidence Against Rejection Accuracy
        CARC depicts the proportion of correct rejections (i.e., target absent lineups where the witness correctly rejects the lineup)
        among all rejections (both correct rejections and false rejections, i.e., target present lineups where the witness incorrectly rejects the lineup) at each confidence level.
        Results stored in data_rates['carc'] (index ('carc','central')).
        '''

        baseRate = self.baseRate

        try:
            r_ta = self.data_pivot.loc['targetAbsent', 'rejectId'].astype(float)
        except KeyError:
            r_ta = _pandas.Series(0.0, index=self.data_pivot.columns)

        try:
            r_tp = self.data_pivot.loc['targetPresent', 'rejectId'].astype(float)
        except KeyError:
            r_tp = _pandas.Series(0.0, index=self.data_pivot.columns)

        numerator = (1.0 - baseRate) * r_ta
        denominator = numerator + baseRate * r_tp
        carc = numerator / denominator

        carc.name = ('carc', 'central')
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(carc).transpose()])
        self.data_rates = self.data_rates.sort_index()

    def calculatePAUC(self, xmax = 1.0) :
        '''         
        Calculate partial area under the curve from (0,0) to (xmax, y(xmax))

        :param xmax: Upper integration limit
        :type xmax: float
        :rtype: float  
        '''

        self.pAUC_xmax = xmax

        if xmax == 1.0 : 
            xmax = self.liberalTargetAbsentSuspectId

        xForIntegration = []
        yForIntegration = []

        # (0,0) for integration 
        xForIntegration.append(0)
        yForIntegration.append(0)

        x = self.data_rates.loc['targetAbsent', 'suspectId'][_np.sort(self.data_rates.columns)[::-1]]
        y = self.data_rates.loc['targetPresent','suspectId'][_np.sort(self.data_rates.columns)[::-1]]
        i = _np.arange(0,len(x),1)

        # rest of range apart from end point for integration 
        xForIntegration.extend(list(x[x<xmax]))
        yForIntegration.extend(list(y[x<xmax]))

        # check xmax is within x data range
        if xmax > x.max() :
            # print("pAUC extrapolating")

            # last point
            x1 = x[-1]
            x2 = 1.0
            y1 = y[-1]
            y2 = 1.0

        elif xmax == x.max() : # edge case where
            i1 = i[-2]
            i2 = i[-1]

            # last point
            x1 = x[i1]
            x2 = x[i2]
            y1 = y[i1]
            y2 = y[i2]

        else :
            i1 = i[x <= xmax][-1]
            i2 = i1+1

            # last point
            x1 = x[i1]
            x2 = x[i2]
            y1 = y[i1]
            y2 = y[i2]

        ymax = (y2-y1)/(x2-x1)*(xmax-x1)+y1

        xForIntegration.append(xmax)
        yForIntegration.append(ymax)

        self.xForIntegration = _np.array(xForIntegration)
        self.yForIntegration = _np.array(yForIntegration)

        # self.pAUC = _integrate.simps(self.yForIntegration,self.xForIntegration, even="avg")
        self.pAUC = _integrate.trapezoid(self.yForIntegration, self.xForIntegration)

        global bPAUCNanWarning

        if _math.isnan(self.pAUC)  and bPAUCNanWarning:
            print("Nan found in PAUC consider rebinning the data, certainly check for the number of NANs")
            print(self.xForIntegration)
            print(self.yForIntegration)
            print(self.pAUC)
            bPAUCNanWarning = False

        return self.pAUC

    def calculateNormalisedAUC(self) :
        pass

    def calculateDPrime(self):

        zT = _special.ndtri(self.data_rates.loc['targetPresent','suspectId'])
        try :
            zL = _special.ndtri(self.data_rates.loc['targetAbsent','suspectId'])
        except : # only for TA showups and the participant never made a suspectId
            zL = _special.ndtri(self.data_rates.loc['targetAbsent','rejectId'])

        dPrime = zT - zL
        dPrime.name = ("dprime", "central")

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(dPrime).transpose()])
        self.data_rates = self.data_rates.sort_index()

        def p0(x, a,b) :
            return a*x+b

        try :
            # TODO remove NaN
            if self.lineupSize == 1 :
                [self.zLzT_fitOpt, self.zLzT_fitCov] = _optimize.curve_fit(p0,zT[0:-1],zL[0:-1])
            else :
                [self.zLzT_fitOpt, self.zLzT_fitCov] = _optimize.curve_fit(p0, zT, zL)

            # TODO think of better naming
            self.sigma_pred = self.zLzT_fitOpt[0]
            self.mu_pred    = -self.zLzT_fitOpt[1]
            self.c_pred     = _special.ndtri(1 - self.data_rates.loc['targetPresent', 'suspectId']) * self.sigma_pred +self.mu_pred
        except:
            pass

        c = _np.array(self.data_rates.columns.get_level_values(self.dependentVariable).values)

        zT_series = _pandas.Series(name=("zT","central"),data=zT)
        zL_series = _pandas.Series(name=("zL","central"),data=zL)

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(zT_series).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(zL_series).transpose()])
        self.data_rates = self.data_rates.sort_index()

        if self.lineupSize == 1 :
            # lowest positive confidence
            posConf = _np.sort(c[c>0])
            lowPosConf = posConf[0]
            self.dPrime = self.data_rates.loc['dprime','central'][self.dependentVariable][lowPosConf]
        else :
            conf = _np.sort(c)
            lowConf = conf[0]
            self.dPrime = self.data_rates.loc['dprime', 'central'][self.dependentVariable][lowConf]

        return dPrime

    def calculateCriterion(self):
        zT = _special.ndtri(self.data_rates.loc['targetPresent','suspectId'])
        try :
            zL = _special.ndtri(self.data_rates.loc['targetAbsent','suspectId'])
        except : # only for TA showups and the participant never made a suspectId
            zL = _special.ndtri(self.data_rates.loc['targetAbsent','rejectId'])

        dCriterion = - (zT + zL)/2.0
        dCriterion.name = ("criterion", "central")
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(dCriterion).transpose()])
        self.data_rates = self.data_rates.sort_index()

    def calculateConfidenceBootstrap(self, nBootstraps = 200, cl = 95, plotROC = False, plotCAC = False, plotCARC = False, pairKey = "participantId", pairs = None) :
        
        # if already bootstrapped delete DataFrame rows
        if self.bootstrapped :
            self.data_rates.drop(("cac","low"),inplace = True)
            self.data_rates.drop(("cac","high"),inplace = True)
            self.data_rates.drop(('carc','low'),inplace = True)
            self.data_rates.drop(('carc','high'),inplace = True)
            self.data_rates.drop(("targetAbsent","fillerId_high"),inplace = True)
            self.data_rates.drop(("targetAbsent","fillerId_low"),inplace = True)
            self.data_rates.drop(("targetAbsent","rejectId_high"),inplace = True)
            self.data_rates.drop(("targetAbsent","rejectId_low"),inplace = True)
            self.data_rates.drop(("targetAbsent","suspectId_high"),inplace = True)
            self.data_rates.drop(("targetAbsent","suspectId_low"),inplace = True)
            self.data_rates.drop(("targetPresent","fillerId_high"),inplace = True)
            self.data_rates.drop(("targetPresent","fillerId_low"),inplace = True)
            self.data_rates.drop(("targetPresent","rejectId_high"),inplace = True)
            self.data_rates.drop(("targetPresent","rejectId_low"),inplace = True)
            self.data_rates.drop(("targetPresent","suspectId_high"),inplace = True)
            self.data_rates.drop(("targetPresent","suspectId_low"),inplace = True)
            self.data_rates.drop(("zL","low"),inplace = True)
            self.data_rates.drop(("zL","high"),inplace = True)
            self.data_rates.drop(("zT","low"),inplace = True)
            self.data_rates.drop(("zT","high"),inplace = True)
            self.data_rates.drop(("dprime","low"),inplace = True)
            self.data_rates.drop(("dprime","high"),inplace = True)
            self.data_rates.drop(("criterion","low"),inplace = True)
            self.data_rates.drop(("criterion","high"),inplace = True)

            try:
                self.data_rates.drop((self.dependentVariable,"low"), inplace=True)
                self.data_rates.drop((self.dependentVariable,"high"), inplace=True)
            except :
                pass

            try:
                self.data_rates.drop(("carc","low"),  inplace=True)
                self.data_rates.drop(("carc","high"), inplace=True)
            except:
                pass


        cac = []
        carc = []
        confidence = []

        targetAbsentFillerId   = []
        targetAbsentRejectId   = []
        targetAbsentSuspectId  = []
        
        targetPresentFillerId  = []
        targetPresentRejectId  = []
        targetPresentSuspectId = []

        zL                     = []
        zT                     = []
        dprime                 = []
        dprime_overall         = []
        pAUC                   = []
        criterion              = []

        if not _np.any(pairs) :
            self.bootstrapPairs = []
        else :
            if nBootstraps > len(pairs) :
                print("only "+str(len(pairs))+" in pairs setting nBootstraps to "+str(len(pairs)))
                nBootstraps = len(pairs)

        for i in range(0,nBootstraps,1) :
            if not _np.any(pairs):
                dr = self.dataRaw.resampleWithReplacement()
                self.bootstrapPairs.append(_np.array(dr.data[pairKey]))
            else :
                dr = self.dataRaw.resampleOnKeyWithReplacement(pairs[i], pairKey)

            # keep hold of last boot strap for debugging
            self.lastbs_dr = dr

            dp = dr.process(self.dataRaw.processColumn,
                            self.dataRaw.processCondition,
                            self.dataRaw.processReverseConfidence,
                            self.dataRaw.pAUCLiberal,
                            self.confidenceLevels,
                            dependentVariable=self.dataRaw.dependentVariable,
                            baseRate=self.baseRate)

            cac.append(dp.data_rates.loc['cac','central'].values)

            try :
                confidence.append(dp.data_rates.loc[self.dependentVariable,'central'].values)
            except :
                pass

            targetAbsentRejectId.append(dp.data_rates.loc['targetAbsent','rejectId'].values)
            targetAbsentSuspectId.append(dp.data_rates.loc['targetAbsent','suspectId'].values)

            if self.lineupSize != 1 :                                                                       # SHOWUP
                targetAbsentFillerId.append(dp.data_rates.loc['targetAbsent','fillerId'].values)
            else :
                targetAbsentFillerId.append(_np.zeros(len(dp.data_rates.loc['targetAbsent','suspectId'].values)))

            targetPresentRejectId.append(dp.data_rates.loc['targetPresent','rejectId'].values)
            targetPresentSuspectId.append(dp.data_rates.loc['targetPresent','suspectId'].values)

            if self.lineupSize != 1 :                                                                       # SHOWUP
                targetPresentFillerId.append(dp.data_rates.loc['targetPresent','fillerId'].values)
            else :
                targetPresentFillerId.append(_np.zeros(len(dp.data_rates.loc['targetPresent','suspectId'].values)))

            zL.append(dp.data_rates.loc['zL','central'].values)
            zT.append(dp.data_rates.loc['zT','central'].values)
            dprime.append(dp.data_rates.loc['dprime','central'].values)
            dprime_overall.append(dp.data_rates.loc[('dprime','central')].values)
            criterion.append(dp.data_rates.loc[('criterion','central')].values)
            pAUC.append(dp.pAUC)

            carc.append(dp.data_rates.loc['carc', 'central'].values)

            if plotROC :
                _plt.figure(1)
                dp.plotROC()

            if plotCAC :
                _plt.figure(2)
                dp.plotCAC()

            if plotCARC:
                _plt.figure(3)
                dp.plotCARC()

        cac                    = _np.array(cac)

        carc                   = _np.array(carc)

        confidence             = _np.array(confidence)

        targetAbsentFillerId   = _np.array(targetAbsentFillerId)
        targetAbsentRejectId   = _np.array(targetAbsentRejectId)
        targetAbsentSuspectId  = _np.array(targetAbsentSuspectId)

        targetPresentFillerId  = _np.array(targetPresentFillerId)
        targetPresentRejectId  = _np.array(targetPresentRejectId)
        targetPresentSuspectId = _np.array(targetPresentSuspectId)

        zL                     = _np.array(zL)
        zT                     = _np.array(zT)
        dprime                 = _np.array(dprime)
        dprime_overall         = _np.array(dprime_overall)
        criterion              = _np.array(criterion)
        pAUC                   = _np.array(pAUC)

        clHigh = 100.-(100.-cl)/2.0
        clLow  = (100.-clHigh)/2.0

        cac_low                     = _np.percentile(cac,clLow,axis=0)
        cac_high                    = _np.percentile(cac,clHigh,axis=0)

        carc_low = _np.percentile(carc, clLow, axis=0)
        carc_high = _np.percentile(carc, clHigh, axis=0)

        confidence_low              = _np.percentile(confidence,clLow,axis=0)
        confidence_high             = _np.percentile(confidence,clHigh,axis=0)

        targetAbsentFillerId_low    = _np.percentile(targetAbsentFillerId,clLow,axis=0)
        targetAbsentFillerId_high   = _np.percentile(targetAbsentFillerId,clHigh,axis=0)

        targetAbsentRejectId_low    = _np.percentile(targetAbsentRejectId,clLow,axis=0)
        targetAbsentRejectId_high   = _np.percentile(targetAbsentRejectId,clHigh,axis=0)

        targetAbsentSuspectId_low   = _np.percentile(targetAbsentSuspectId,clLow,axis=0)
        targetAbsentSuspectId_high  = _np.percentile(targetAbsentSuspectId,clHigh,axis=0)  

        targetPresentFillerId_low   = _np.percentile(targetPresentFillerId,clLow,axis=0)                 # No for showups (TODO)
        targetPresentFillerId_high  = _np.percentile(targetPresentFillerId,clHigh,axis=0)                # No for showups (TODO)

        targetPresentRejectId_low   = _np.percentile(targetPresentRejectId,clLow,axis=0)
        targetPresentRejectId_high  = _np.percentile(targetPresentRejectId,clHigh,axis=0)

        targetPresentSuspectId_low  = _np.percentile(targetPresentSuspectId,clLow,axis=0)
        targetPresentSuspectId_high = _np.percentile(targetPresentSuspectId,clHigh,axis=0)        

        zL_low                      = _np.percentile(zL,clLow,axis=0)
        zL_high                     = _np.percentile(zL,clHigh,axis=0)
        zT_low                      = _np.percentile(zT,clLow,axis=0)
        zT_high                     = _np.percentile(zT,clHigh,axis=0)
        dprime_low                  = _np.percentile(dprime,clLow,axis=0)
        dprime_high                 = _np.percentile(dprime,clHigh,axis=0)
        criterion_low               = _np.percentile(criterion,clLow,axis=0)
        criterion_high              = _np.percentile(criterion,clHigh,axis=0)

        self.pAUC_low               = _np.percentile(pAUC[_np.logical_not(_np.isnan(pAUC))],clLow)
        self.pAUC_high              = _np.percentile(pAUC[_np.logical_not(_np.isnan(pAUC))],clHigh)
        self.pAUC_array             = pAUC
        self.criterion_array        = criterion
        self.dprime_array           = dprime_overall

        template = self.data_rates.loc['cac','central']
        self.data_rates = _pandas.concat([self.data_rates,_pandas.DataFrame(_pandas.Series(cac_low, name = ('cac','low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates,_pandas.DataFrame(_pandas.Series(cac_high, name = ('cac','high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([
            self.data_rates,
            _pandas.DataFrame([carc_low], index=[('carc', 'low')],
                              columns=self.data_rates.loc['carc', 'central'].index),
            _pandas.DataFrame([carc_high], index=[('carc', 'high')],
                              columns=self.data_rates.loc['carc', 'central'].index),
        ])

        try :
            self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(confidence_low, name = (self.dependentVariable,'low'), index = template.index)).transpose()])
            self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(confidence_high, name = (self.dependentVariable,'high'), index = template.index)).transpose()])
        except :
            pass

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetAbsentFillerId_low, name = ('targetAbsent','fillerId_low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetAbsentFillerId_high, name = ('targetAbsent','fillerId_high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetAbsentRejectId_low, name = ('targetAbsent','rejectId_low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetAbsentRejectId_high, name = ('targetAbsent','rejectId_high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetAbsentSuspectId_low, name = ('targetAbsent','suspectId_low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetAbsentSuspectId_high, name = ('targetAbsent','suspectId_high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetPresentFillerId_low, name = ('targetPresent','fillerId_low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetPresentFillerId_high, name = ('targetPresent','fillerId_high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetPresentRejectId_low, name = ('targetPresent','rejectId_low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetPresentRejectId_high, name = ('targetPresent','rejectId_high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetPresentSuspectId_low, name = ('targetPresent','suspectId_low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(targetPresentSuspectId_high, name = ('targetPresent','suspectId_high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(zL_low,  name = ('zL','low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(zL_high, name = ('zL','high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(zT_low,  name = ('zT','low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(zT_high, name = ('zT','high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(dprime_low,  name = ('dprime','low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(dprime_high, name = ('dprime','high'), index = template.index)).transpose()])

        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(criterion_low,  name = ('criterion','low'), index = template.index)).transpose()])
        self.data_rates = _pandas.concat([self.data_rates, _pandas.DataFrame(_pandas.Series(criterion_high, name = ('criterion','high'), index = template.index)).transpose()])

        self.data_rates = self.data_rates.sort_index()

        self.bootstrapped = True

        if not _np.any(pairs) :
            self.bootstrapPairs = _np.array(self.bootstrapPairs)

    def comparePAUC(self, other, useCovariance=False):
        '''
        Statistical test compare two pAUCs

        :param other: object to compare against
        :type other: DataProcessed
        :return:
        '''

        pAUC1 = self.pAUC_array
        pAUC2 = other.pAUC_array

        # strip nan (not right TODO regarding pAUC integrals, also and of NaNs for pairs)
        pAUC1 = pAUC1[_np.logical_not(_np.isnan(pAUC1))]
        pAUC2 = pAUC2[_np.logical_not(_np.isnan(pAUC2))]

        pAUC1_mean = pAUC1.mean()
        pAUC1_std  = pAUC1.std()
        pAUC2_mean = pAUC2.mean()
        pAUC2_std  = pAUC2.std()

        if useCovariance:
            cov = _np.cov(pAUC1, pAUC2)[0,1]
            print(cov)
        else :
            cov = 0
            print(cov)

        denom = _np.sqrt(pAUC1_std**2 + pAUC2_std**2 - 2*cov)
        D = _np.abs(self.pAUC - other.pAUC)/denom
        p = (1-_special.ndtr(D))*2

        print('DataProcessed.comparePAUC> pAUC1'.ljust(self.debugIoPadSize,' ')+":",round(self.pAUC,4), "+/-",round(pAUC1_std,4))
        print('DataProcessed.comparePAUC> pAUC2'.ljust(self.debugIoPadSize,' ')+":",round(other.pAUC,4),"+/-",round(pAUC2_std,4))
        print('DataProcessed.comparePAUC> covariance'.ljust(self.debugIoPadSize,' ')+":",cov)
        print('DataProcessed.comparePAUC> Z, p'.ljust(self.debugIoPadSize,' ')+":",round(D,4),round(p,4))
        print('DataProcessed.comparePAUC> pooled sd'.ljust(self.debugIoPadSize,' ')+":",denom)
        return [D,p]

    def compareCriterion(self, other):
        '''
        Statistical test compare two criteria

        :param other: object to compare against
        :type other: DataProcessed
        :return:
        '''

        criterion1 = self.criterion_array
        criterion2 = other.criterion_array

        # strip nan (not right TODO regarind pAUC integrals)
        criterion1 = criterion1[_np.logical_not(_np.isnan(criterion1))]
        criterion2 = criterion2[_np.logical_not(_np.isnan(criterion2))]

        criterion1_mean = criterion1.mean()
        criterion1_std  = criterion1.std()
        criterion2_mean = criterion2.mean()
        criterion2_std  = criterion2.std()

        D = _np.abs(criterion1_mean - criterion2_mean)/_np.sqrt(criterion1_std**2 + criterion2_std**2)
        p = (1-_special.ndtr(D))*2

        print('DataProcessed.compareCriterion> criterion1'.ljust(self.debugIoPadSize,' ')+":",round(criterion1_mean,4), "+/-",round(criterion1_std,4))
        print('DataProcessed.compareCriterion> criterion2'.ljust(self.debugIoPadSize,' ')+":",round(criterion2_mean,4),"+/-",round(criterion2_std,4))
        print('DataProcessed.compareCriterion> Z, p'.ljust(self.debugIoPadSize,' ')+":",round(D,4),round(p,4))
        print('DataProcessed.compareCriterion> pooled sd',_np.sqrt(criterion1_std**2 + criterion2_std**2))

        return [D,p]

    def compareDprime(self, other):
        '''
        Statistical test compare two Dprimes

        :param other: object to compare against
        :type other: DataProcessed
        :return:
        '''

        dprime1 = self.dprime_array
        dprime2 = other.dprime_array

        # strip nan (not right TODO regarind pAUC integrals)
        dprime1 = dprime1[_np.logical_not(_np.isnan(dprime1))]
        dprime2 = dprime2[_np.logical_not(_np.isnan(dprime2))]

        dprime1_mean = dprime1.mean()
        dprime1_std  = dprime1.std()
        dprime2_mean = dprime2.mean()
        dprime2_std  = dprime2.std()

        D = _np.abs(dprime1_mean - dprime2_mean)/_np.sqrt(dprime1_std**2 + dprime2_std**2)
        p = (1-_special.ndtr(D))*2

        print('DataProcessed.comparedprime> dprime1'.ljust(self.debugIoPadSize,' ')+":",round(dprime1_mean,4), "+/-",round(dprime1_std,4))
        print('DataProcessed.comparedprime> dprime2'.ljust(self.debugIoPadSize,' ')+":",round(dprime2_mean,4),"+/-",round(dprime2_std,4))
        print('DataProcessed.comparedprime> Z, p'.ljust(self.debugIoPadSize,' ')+":",round(D,4),round(p,4))
        print('DataProcessed.comparedprime> pooled sd',_np.sqrt(dprime1_std**2 + dprime2_std**2))

        return [D,p]

    def plotROC(self, label = "ROC", relativeFrequencyScale = 800, errorType = 'bars', color = None, alpha = 1, edgecolor = None) :
        '''
        Plot the receiver operating characteristic (ROC) for the data. The symbol size is proportional to 
        relative frequency. If confidence limits are calculated using calculateConfidenceBootstrap they
        are also plotted

        :param label: plot label for legends 
        :type label: str
        :param relativeFrequencyScale: scale of relative frequency (RF) to symbol size.
        :type relativeFrequencyScale: float
        :rtype: None

        '''

        x = _np.linspace(0,1,100)

        _plt.plot(x,x,"--",color="black",linewidth=1.0)
        scatter = _plt.scatter(self.data_rates.loc['targetAbsent', 'suspectId'],
                               self.data_rates.loc['targetPresent','suspectId'],
                               s = self.data_rates.loc['rf','']*relativeFrequencyScale,
                               label = label, color = color, alpha = alpha, edgecolor = edgecolor)
        
        # Plot errors if they have been calculated
        try : 
            if errorType == 'bars' : 
                _plt.errorbar(self.data_rates.loc['targetAbsent', 'suspectId'],
                              self.data_rates.loc['targetPresent','suspectId'],
                              xerr = [self.data_rates.loc['targetAbsent', 'suspectId'] - self.data_rates.loc['targetAbsent', 'suspectId_low'],
                                      self.data_rates.loc['targetAbsent', 'suspectId_high'] - self.data_rates.loc['targetAbsent', 'suspectId']],                        
                              yerr = [self.data_rates.loc['targetPresent','suspectId'] - self.data_rates.loc['targetPresent','suspectId_low'],
                                      self.data_rates.loc['targetPresent','suspectId_high']- self.data_rates.loc['targetPresent','suspectId']],
                              fmt='.',
                              color=scatter.get_facecolor()[0],
                              ecolor=scatter.get_facecolor()[0],
                              capsize=5, alpha = alpha)
            elif errorType == 'band' : 
                _plt.fill_between(self.data_rates.loc['targetAbsent', 'suspectId'],
                                  self.data_rates.loc['targetPresent', 'suspectId_low'],
                                  self.data_rates.loc['targetPresent', 'suspectId_high'],
                                  alpha=0.25)
        except KeyError :
            pass

        # shade ROC pAUC 
        if self.pAUC_xmax != 1 :
            _plt.fill_between(self.xForIntegration, 
                              _np.zeros(self.xForIntegration.size), 
                              self.yForIntegration,
                              interpolate=True,
                              alpha=0.25,
                              color=scatter.get_facecolor()[0])
         
        xmin = self.data_rates.loc['targetAbsent', 'suspectId'].min()
        xmax = self.data_rates.loc['targetAbsent', 'suspectId'].max()
        xdif = xmax - xmin

        ymin = self.data_rates.loc['targetPresent','suspectId'].min()
        ymax = self.data_rates.loc['targetPresent','suspectId'].max()
        ydif = ymax - ymin
        
        ax = _plt.gca()
        ax.set_xlim(0, xmax+xdif*0.1)
        ax.set_ylim(0, ymax+ydif*0.1)
             
        _plt.xlabel("False ID rate")
        _plt.ylabel("Correct ID rate")
        
        # Tight layout for plot
        _plt.tight_layout()

    def plotCAC(self, relativeFrequencyScale = 800, errorType = 'bars', color = None, label= "", oldLabels = None, newLabels = None, alpha = 1) :
        '''
        Plot the confidence accuracy characteristic (CAC) for the data. The symbol size is proportional to 
        relative frequency. If confidence limits are calculated using calculateConfidenceBootstrap they
        are also plotted.
        
        :param label: plot label for legends 
        :type label: str
        :param relativeFrequencyScale: scale of relative frequncy (RF) to symbol size.
        :type rellativeFrequencyScale: float
        :rtype: None
        
        '''

        confidence = self.data_rates.columns.get_level_values(self.dependentVariable)
        cac        = self.data_rates.loc['cac','central']
        rf         = self.data_rates.loc['rf','']

        # try average confidence (if calculated)
        try :
            confidence = self.data_rates.loc[self.dependentVariable,'central']
        except :
            pass

        # Basic scatter plot
        scatter = _plt.scatter(confidence,cac,s = rf*relativeFrequencyScale,label = label,color = color, alpha = alpha)
        
        # Plot errors if they have been calculated
        try : 
            if errorType == 'bars' : 
                scatterErr = _plt.errorbar(confidence,cac,
                                           yerr = [self.data_rates.loc['cac','central']-self.data_rates.loc['cac','low'],
                                                   self.data_rates.loc['cac','high']-self.data_rates.loc['cac','central']],
                                           xerr = [self.data_rates.loc[self.dependentVariable,'central']-self.data_rates.loc[self.dependentVariable,'low'],
                                                     self.data_rates.loc[self.dependentVariable,'high']-self.data_rates.loc[self.dependentVariable,'central']],
                                           fmt='.',
                                           color  = scatter.get_facecolor()[0],
                                           ecolor = scatter.get_facecolor()[0],
                                           capsize=5,
                                           alpha=alpha)


            elif errorType == 'band' : 
                _plt.fill_between(confidence,
                                  self.data_rates.loc['cac','low'],
                                  self.data_rates.loc['cac','high'],
                                  alpha=0.25)
        except KeyError :
            pass

        _plt.xlabel("Confidence")
        _plt.ylabel("Proportion correct") 
        
        if self.reverseConfidence :
            ax = _plt.gca()
            lx = ax.get_xlim()
            ax.set_xlim([lx[1],lx[0]])
        else : 
            ax = _plt.gca()
            
            xmin = confidence.min()
            xmax = confidence.max()
            xdif = xmax-xmin 

            ymin = cac.min()
            ymax = cac.max()
            ydif = ymax-ymin
             
            ax.set_xlim(xmin-xdif*0.1, xmax+xdif*0.1)
            ax.set_ylim(ymin-ydif*0.1, ymax+ydif*0.1)
        
        if newLabels and oldLabels :
            ax.set_xticks(oldLabels,labels=newLabels)
        
        # Tight layout for plot
        _plt.tight_layout()

    def plotCARC(self, relativeFrequencyScale=800, errorType='bars', label="", oldLabels=None, newLabels=None, alpha=1, color=None):
        """
        pLOT Confidence–Accuracy Characteristic for lineup rejections (CARC)
        The symbol size is proportional to relative frequency of all rejections (TA+TP).
        If calculateConfidenceBootstrap has been run, error bars/bands are also plotted.

        Parameters
        ----------
        relativeFrequencyScale : float
        errorType : {'bars', 'band', None}
        label : str
        oldLabels, newLabels : list[str] or None (If provided, replace x-axis tick labels from oldLabels to newLabels.)
        alpha : float
        """
        # x: confidence levels
        try:
            confidence = self.data_rates.loc[self.dependentVariable, 'central']
        except Exception:
            confidence = self.data_rates.columns.get_level_values(self.dependentVariable)

        carc        = self.data_rates.loc['carc', 'central']
        rf_reject   = self.data_rates.loc['rf_reject', '']

        # Plot scatter
        scatter = _plt.scatter(confidence, carc, s=rf_reject.values * relativeFrequencyScale, label=label, color=color, alpha=alpha)

        # Plot errors if have been calculated
        try:
            if errorType == 'bars':
                yerr = [
                    self.data_rates.loc['carc', 'central'] - self.data_rates.loc['carc', 'low'],
                    self.data_rates.loc['carc', 'high'] - self.data_rates.loc['carc', 'central'],
                ]
                try:
                    xerr = [
                        self.data_rates.loc[self.dependentVariable, 'central'] - self.data_rates.loc[
                            self.dependentVariable, 'low'],
                        self.data_rates.loc[self.dependentVariable, 'high'] - self.data_rates.loc[
                            self.dependentVariable, 'central'],
                    ]
                except KeyError:
                    xerr = None

                _plt.errorbar(
                    confidence, carc,
                    yerr=yerr, xerr=xerr,
                    fmt='.',
                    color=scatter.get_facecolor()[0],
                    ecolor=scatter.get_facecolor()[0],
                    capsize=5, alpha=alpha
                )
            elif errorType == 'band':
                _plt.fill_between(confidence, self.data_rates.loc['carc', 'low'], self.data_rates.loc['carc', 'high'],
                                  alpha=0.25)
        except KeyError:
            pass

        _plt.xlabel("Confidence")
        _plt.ylabel("Proportion of correct rejections")

        if self.reverseConfidence:
            ax = _plt.gca()
            lx = ax.get_xlim()
            ax.set_xlim([lx[1], lx[0]])
        else:
            ax = _plt.gca()

            xmin = confidence.min()
            xmax = confidence.max()
            xdif = xmax - xmin

            ymin = carc.min()
            ymax = carc.max()
            ydif = ymax - ymin

            ax.set_xlim(xmin - xdif * 0.1, xmax + xdif * 0.1)
            ax.set_ylim(ymin - ydif * 0.1, ymax + ydif * 0.1)

        if newLabels and oldLabels:
            ax.set_xticks(oldLabels, labels=newLabels)

        _plt.tight_layout()

    def plotRAC(self) :
        pass

    def plotHitVsFalseAlarmRate(self):

        zL = self.data_rates.loc["zL", "central"]
        zT = self.data_rates.loc["zT", "central"]

        # TODO remove NaN
        if self.lineupSize == 1 :
            zT_pred = _np.linspace(zT.min(),zT[0:-1].max(),100)
        else :
            zT_pred = _np.linspace(zT.min(),zT.max(),100)

        zL_pred = zT_pred*self.zLzT_fitOpt[0]+self.zLzT_fitOpt[1]

        _plt.plot(zT,zL,"o",label="Data")
        _plt.plot(zT_pred,zL_pred,"--",label="Linear fit")

        # _plt.grid(True)
        _plt.legend()
        _plt.xlabel("$Z_{\\rm HR}$")
        _plt.ylabel("$Z_{\\rm FAR}$")
        _plt.tight_layout()

    def printPivot(self) :
        print(self.data_pivot)
        print("total number of participants",self.data_pivot.sum().sum())

    def printRates(self) :
        print(self.data_rates)

    def printDescriptiveStats(self):
        print('Number of lineups',self.numberLineups)
        print('Number of target-absent lineups',self.numberTALineups)
        print('Number of target-present lineups',self.numberTPLineups)
        print('Correct ID rate',self.data_rates.loc[("targetPresent", "suspectId")].max())
        print('False ID rate',self.data_rates.loc[("targetAbsent", "suspectId")].max())
        print('dPrime',self.dPrime)
        print('pAUC',self.pAUC)

    def isDesignateId(self):
        try:
            self.data_pivot.loc['targetAbsent', 'designateId']
            return True
        except KeyError:
            return False

    @property
    def numberConditions(self) :
        '''
        Number of confidences or other conditions 

        :rtype: int 
        '''
        return self.data_rates.columns.get_level_values(self.dependentVariable).size

    @property
    def numberLineups(self):
        return self.numberTALineups + self.numberTPLineups

    @property
    def liberalTargetAbsentSuspectId(self) :
        '''
        Returns the maximum targetAbsent suspectId rate 

        :rtype: float 
        '''

        return self.data_rates.loc['targetAbsent','suspectId'].max()

    @property 
    def liberalTargetAbsentFillerId(self) : 
        '''
        Returns the maximum targetAbsent falseId rate 

        :rtype: float 
        '''

        return self.data_rates.loc['targetAbsent','fillerId'].max()        

    def writeRatesCsv(self, fileName) : 
        '''
        Write data_rates Dataframe to CSV file 
        :rtype: None
        '''

        self.data_rates.to_csv(fileName)

    def writeRatesExcel(self, fileName, engine = 'openpyxl') : 
        '''
        Write data_rates Dataframe to excel file 

        :param fileName: File name of the excel file to write
        :type fileName: str
        :param engine: Excel output engine
        :type engine: str
        :rtype: None
        '''

        self.data_rates.to_excel(fileName, engine = engine)        

    def writePivotCsv(self, fileName) : 
        '''
        Write data_rates Dataframe to CSV file 

        :param fileName: File name of the CSV file to write
        :type fileName: str
        :rtype: None

        '''

        self.data_pivot.to_csv(fileName)

    def writePivotSimpleCsv(self, fileName) : 
        '''
        Write data_pivot Dataframe to CSV file 

        :param fileName: File name of the CSV file to write
        :type fileName: str
        :rtype: None

        '''

        pass

    def writePivotExcel(self, fileName, engine = 'openpyxl') :
        '''
        Write data_pivot Dataframe to excel file 

        :param fileName: File name of the excel file to write        
        :type fileName: str
        :param engine: Excel output engine
        :type engine: str
        :rtype: None

        '''

        self.data_pivot.to_excel(fileName, engine = engine)
