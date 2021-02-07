import pandas as _pandas
import matplotlib.pyplot as _plt
import numpy as _np
import scipy.integrate as _integrate
import copy as _copy

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
    
    def __init__(self, dataRaw, reverseConfidence = False, lineupSize = 1) : 
        
        if isinstance(dataRaw, str) :
            # could just load the data frame from csv, but want to have in exactly same format. 

            data_pivot_load = _pandas.read_csv(data_pivot)

            nrows = data_pivot_load.shape[0]
            
            # columns 
            columns = data_pivot_load.columns.values[1:]

            print(columns)

            # loop over rows
            for i in range(0,nrows,1) : 
                rowLabel = data_pivot_load.iloc[i].values[0]
                rowData  = data_pivot_load.iloc[i].values[1:] 
                print(rowLabel, rowData)
        else :
            self.dataRaw           = dataRaw
            self.lineupSize        = lineupSize 
            self.reverseConfidence = reverseConfidence
            self.calculatePivot()
            self.numberTPLineups   = self.data_pivot.loc['targetPresent'].sum().sum()
            self.numberTALineups   = self.data_pivot.loc['targetAbsent'].sum().sum()

        self.calculateRates(reverseConfidence)
        self.calculateConfidence()
        self.calculateRelativeFrequency()
        self.calculateCAC()
        self.calculatePAUC()

        self.bootstrapped = False

    def calculatePivot(self) : 
        ''' 
        Calculate fequency pivot table against 'confidence'

        :rtype: None
        '''
        
        self.data_pivot = _pandas.pivot_table(self.dataRaw.dataSelected, 
                                              columns='confidence', 
                                              index=['targetLineup','responseType'], 
                                              aggfunc={'confidence':'count'})


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

    def calculateRates(self, reverseConfidence = False) :
        ''' 
        Calculate cumulative rates from data_pivot. Result stored in data_rates
        
        :param reverseConfidence: Flag true if confidence increases with lower values
        :type reverseConfidence: bool
        :rtype: None
        '''
        
        self.data_rates = self.data_pivot.copy()

        # reverse confidence
        self.reverseConfidence = reverseConfidence
        if not reverseConfidence : 
            columns = self.data_rates.columns.tolist()
            columns = columns[::-1]
            self.data_rates = self.data_rates[columns]

        # cumulative rates
        self.data_rates = self.data_rates.cumsum(1)

        self.targetAbsentSum   = self.data_pivot.loc['targetAbsent'].sum().sum()
        self.targetPresentSum  = self.data_pivot.loc['targetPresent'].sum().sum()
        
        try :
            self.data_rates.loc['targetAbsent','fillerId']  = self.data_rates.loc['targetAbsent','fillerId']/self.targetAbsentSum          
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
            suspectId = self.data_rates.loc['targetAbsent','fillerId']/self.lineupSize
            suspectId.name = ("targetAbsent","suspectId")
            self.data_rates = self.data_rates.append(suspectId)
            self.data_rates = self.data_rates.sort_index()

    def calculateConfidence(self):

        '''
        Calculate average confidence for a bin. Result stored in data_rates['confidence']
        '''

        confidence_mean = _copy.copy(self.data_rates.loc['targetAbsent','fillerId'])
        confidence_mean.name = ("confidence","central")

        if self.dataRaw and self.dataRaw.collapseContinuous :
            for i in range(0,len(self.dataRaw.collapseContinuousLabels)) :
                label = self.dataRaw.collapseContinuousLabels[i]
                conf_label = self.dataRaw.data['confidence_original'][self.dataRaw.data['confidence'] == label]
                conf_mean  = conf_label.mean()

                confidence_mean[len(self.dataRaw.collapseContinuousLabels)-i-1] = conf_mean

            self.data_rates = self.data_rates.append(confidence_mean)
            self.data_rates = self.data_rates.sort_index()

    def calculateRelativeFrequency(self) :

        '''
        Calculate relative frequency from data_pivot. Result stored in data_rates['cf']
        '''

        if self.lineupSize != 1 :                                                                           # SHOWUP
            cid = self.data_pivot.loc['targetPresent','suspectId']
        else :
            cid = self.data_pivot.loc['targetPresent','suspectId'] + self.data_pivot.loc['targetPresent','rejectId']

        try :
            if self.lineupSize != 1 :                                                                       # SHOWUP
                fid = self.data_pivot.loc['targetAbsent','suspectId']
            else :
                fid = self.data_pivot.loc['targetAbsent','suspectId'] + self.data_pivot.loc['targetAbsent','rejectId']
        except KeyError :            
            fid = self.data_pivot.loc['targetAbsent','fillerId']/self.lineupSize

        rf = (cid + fid)/(cid.sum() + fid.sum())
        rf.name = ("rf","") 
        self.data_rates = self.data_rates.append(rf)
        self.data_rates = self.data_rates.sort_index()

    def calculateCAC(self) :

        '''
        Calculate confidence accuracy characteristic from data_pivot. Result stored in data_rates['cac']
        '''

        if self.lineupSize != 1 :                                                                           # SHOWUP
            cid = self.data_pivot.loc['targetPresent','suspectId']
        else :
            cid = self.data_pivot.loc['targetPresent', 'suspectId'] + self.data_pivot.loc['targetPresent', 'rejectId']

        try :
            if self.lineupSize != 1 :                                                                       # SHOWUP
                fid = self.data_pivot.loc['targetAbsent','suspectId']
            else :
                fid = self.data_pivot.loc['targetAbsent', 'suspectId'] + self.data_pivot.loc['targetAbsent', 'rejectId']
        except KeyError :            
            fid = self.data_pivot.loc['targetAbsent','fillerId']/self.lineupSize
        
        cac = cid/(cid+fid)
        cac.name = ("cac","central")
        self.data_rates = self.data_rates.append(cac)
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

        x = self.data_rates.loc['targetAbsent', 'suspectId']
        y = self.data_rates.loc['targetPresent','suspectId']
        i = _np.arange(0,len(x),1)

        # rest of range apart from end point for integration 
        xForIntegration.extend(list(x[x<xmax]))
        yForIntegration.extend(list(y[x<xmax]))
        
        # check xmax is within x data range 
        if xmax > x.max() :
            raise IndexError("xmax of "+str(xmax)+" is larger than largest "+str(x.max()))
        elif xmax == x.max() : # edge case where
            i1 = i[-2]
            i2 = i[-1]
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

        self.pAUC = _integrate.simps(self.yForIntegration,self.xForIntegration)

        return self.pAUC

    def calculateNormalisedAUC(sef) : 
        pass

    def calculateConfidenceBootstrap(self, nBootstraps = 200, cl = 95, plotROC = False) :
        
        # if already bootstrapped delete DataFrame rows
        if self.bootstrapped :
            self.data_rates.drop(("cac","low"),inplace = True)
            self.data_rates.drop(("cac","high"),inplace = True)
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

            try:
                self.data_rates.drop(("confidence","low"), inplace=True)
                self.data_rates.drop(("confidence","high"), inplace=True)
            except :
                pass

        cac = []
        confidence = []

        targetAbsentFillerId   = []
        targetAbsentRejectId   = []
        targetAbsentSuspectId  = []
        
        targetPresentFillerId  = []
        targetPresentRejectId  = []
        targetPresentSuspectId = []

        pAUC = []

        for i in range(0,nBootstraps,1) : 
            dr = self.dataRaw.resampleWithReplacement()
            dp = dr.process(self.dataRaw.processColumn, self.dataRaw.processCondition, self.dataRaw.processReverseConfidence)

            cac.append(dp.data_rates.loc['cac','central'].values)

            try :
                confidence.append(dp.data_rates.loc['confidence','central'].values)
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

            pAUC.append(dp.pAUC)
            
            if plotROC : 
                _plt.scatter(dp.data_rates.loc['targetAbsent','suspectId'],
                             dp.data_rates.loc['targetPresent','suspectId'])

        cac                    = _np.array(cac)

        confidence             = _np.array(confidence)

        targetAbsentFillerId   = _np.array(targetAbsentFillerId)
        targetAbsentRejectId   = _np.array(targetAbsentRejectId)
        targetAbsentSuspectId  = _np.array(targetAbsentSuspectId)

        targetPresentFillerId  = _np.array(targetPresentFillerId)
        targetPresentRejectId  = _np.array(targetPresentRejectId)
        targetPresentSuspectId = _np.array(targetPresentSuspectId)

        pAUC                   = _np.array(pAUC) 

        clHigh = cl 
        clLow  = 100-clHigh

        cac_low                     = _np.percentile(cac,clLow,axis=0)
        cac_high                    = _np.percentile(cac,clHigh,axis=0)

        try :
            confidence_low              = _np.percentile(confidence,clLow,axis=0)
            confidence_high             = _np.percentile(confidence,clHigh,axis=0)
        except :
            pass

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

        self.pAUC_low               = _np.percentile(pAUC,clLow)
        self.pAUC_high              = _np.percentile(pAUC,clHigh)
                
        template = self.data_rates.loc['cac','central']
        self.data_rates = self.data_rates.append(_pandas.Series(cac_low, name = ('cac','low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(cac_high, name = ('cac','high'), index = template.index))

        try :
            self.data_rates = self.data_rates.append(_pandas.Series(confidence_low, name = ('confidence','low'), index = template.index))
            self.data_rates = self.data_rates.append(_pandas.Series(confidence_high, name = ('confidence','high'), index = template.index))
        except :
            pass

        self.data_rates = self.data_rates.append(_pandas.Series(targetAbsentFillerId_low, name = ('targetAbsent','fillerId_low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(targetAbsentFillerId_high, name = ('targetAbsent','fillerId_high'), index = template.index))

        self.data_rates = self.data_rates.append(_pandas.Series(targetAbsentRejectId_low, name = ('targetAbsent','rejectId_low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(targetAbsentRejectId_high, name = ('targetAbsent','rejectId_high'), index = template.index))

        self.data_rates = self.data_rates.append(_pandas.Series(targetAbsentSuspectId_low, name = ('targetAbsent','suspectId_low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(targetAbsentSuspectId_high, name = ('targetAbsent','suspectId_high'), index = template.index))

        self.data_rates = self.data_rates.append(_pandas.Series(targetPresentFillerId_low, name = ('targetPresent','fillerId_low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(targetPresentFillerId_high, name = ('targetPresent','fillerId_high'), index = template.index))

        self.data_rates = self.data_rates.append(_pandas.Series(targetPresentRejectId_low, name = ('targetPresent','rejectId_low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(targetPresentRejectId_high, name = ('targetPresent','rejectId_high'), index = template.index))

        self.data_rates = self.data_rates.append(_pandas.Series(targetPresentSuspectId_low, name = ('targetPresent','suspectId_low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(targetPresentSuspectId_high, name = ('targetPresent','suspectId_high'), index = template.index))

        self.data_rates = self.data_rates.sort_index()

        self.bootstrapped = True

    def plotROC(self, label = "ROC", relativeFrequencyScale = 400, errorType = 'bars') :
        '''
        Plot the receiver operating characteristic (ROC) for the data. The symbol size is proportional to 
        relative frequency. If confidence limits are calculated using calculateConfidenceBootstrap they
        are also plotted

        :param label: plot label for legends 
        :type label: str
        :param relativeFrequencyScale: scale of relative frequncy (RF) to symbol size.
        :type rellativeFrequencyScale: float
        :rtype: None

        '''

        x = _np.linspace(0,1,100)

        _plt.plot(x,x,"--",color="black",linewidth=1.0)
        _plt.scatter(self.data_rates.loc['targetAbsent', 'suspectId'],
                     self.data_rates.loc['targetPresent','suspectId'],
                     s = self.data_rates.loc['rf','']*relativeFrequencyScale,
                     label = label)
        
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
                              capsize=5)
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
                              alpha=0.25)
         
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

    def plotCAC(self, label = "CAC", relativeFrequencyScale = 400, errorType = 'bars') :
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

        confidence = self.data_rates.columns.get_level_values('confidence')
        cac        = self.data_rates.loc['cac','central']
        rf         = self.data_rates.loc['rf','']

        # try average confidence (if calculated)
        try :
            confidence = self.data_rates.loc['confidence','central']
        except :
            pass

        # Basic scatter plot
        _plt.scatter(confidence,cac,s = rf*relativeFrequencyScale,label = label)
        
        # Plot errors if they have been calculated
        try : 
            if errorType == 'bars' : 
                _plt.errorbar(confidence,cac,
                              yerr = [self.data_rates.loc['cac','central']-self.data_rates.loc['cac','low'],
                                      self.data_rates.loc['cac','high']-self.data_rates.loc['cac','central']],
                              xerr = [self.data_rates.loc['confidence','central']-self.data_rates.loc['confidence','low'],
                                      self.data_rates.loc['confidence','high']-self.data_rates.loc['confidence','central']],
                              fmt='.',
                              capsize=5)
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
             
        # Tight layout for plot
        _plt.tight_layout()
            
    def plotRAC(self) : 
        pass

    def printPivot(self) :
        print(self.data_pivot)

    def printRates(self) :
        print(self.data_rates)

    @property
    def numberConditions(self) :
        '''
        Number of confidences or other conditions 

        :rtype: int 
        '''
        return self.data_rates.columns.get_level_values('confidence').size

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