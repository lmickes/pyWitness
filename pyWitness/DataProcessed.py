import pandas as _pandas
import matplotlib.pyplot as _plt
import numpy as _np

class DataProcessed :
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
        self.calculateRelativeFrequency()
        self.calculateCAC()

    def calculatePivot(self) : 
        self.data_pivot = _pandas.pivot_table(self.dataRaw.dataSelected, 
                                              columns='confidence', 
                                             index=['targetLineup','responseType'], 
                                             aggfunc={'confidence':'count'})

    def calculateRates(self, reverseConfidence = False) :
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
            self.data_rates.loc['targetAbsent','suspectId'] = self.data_rates.loc['targetAbsent','suspectId']/self.targetAbsentSum
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
            self.data_rates.loc['targetPresent','suspectId'] = self.data_rates.loc['targetPresent','suspectId']/self.targetPresentSum
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

    def calculateRelativeFrequency(self) :
        cid = self.data_pivot.loc['targetPresent','suspectId']         
        try :
            fid = self.data_pivot.loc['targetAbsent','suspectId']
        except KeyError :            
            fid = self.data_pivot.loc['targetAbsent','fillerId']/self.lineupSize

        rf = (cid + fid)/(cid.sum() + fid.sum())
        rf.name = ("rf","") 
        self.data_rates = self.data_rates.append(rf)
        self.data_rates = self.data_rates.sort_index()

    def calculateCAC(self) :
        cid = self.data_pivot.loc['targetPresent','suspectId'] 

        try :
            fid = self.data_pivot.loc['targetAbsent','suspectId']
        except KeyError :            
            fid = self.data_pivot.loc['targetAbsent','fillerId']/self.lineupSize
        
        cac = cid/(cid+fid)
        cac.name = ("cac","central")
        self.data_rates = self.data_rates.append(cac)
        self.data_rates = self.data_rates.sort_index()      

    def calculatePAUC(self) : 
        pass

    def calculateConfidenceBootstrap(self, nBootstraps = 200, cl = 95) :

        cac = []
        targetAbsentFillerId   = []
        targetAbsentRejectId   = []
        targetAbsentSuspectId  = []
        
        targetPresentFillerId  = []
        targetPresentRejectId  = []
        targetPresentSuspectId = []

        for i in range(0,nBootstraps,1) : 
            dr = self.dataRaw.resampleWithReplacement()
            dp = dr.process()
            cac.append(dp.data_rates.loc['cac'].values[0])
            targetAbsentFillerId.append(dp.data_rates.loc['targetAbsent','fillerId'].values)
            targetAbsentRejectId.append(dp.data_rates.loc['targetAbsent','rejectId'].values)
            targetAbsentSuspectId.append(dp.data_rates.loc['targetAbsent','suspectId'].values)

            targetPresentFillerId.append(dp.data_rates.loc['targetPresent','fillerId'].values)
            targetPresentRejectId.append(dp.data_rates.loc['targetPresent','rejectId'].values)
            targetPresentSuspectId.append(dp.data_rates.loc['targetPresent','suspectId'].values)
            
        cac                   = _np.array(cac)

        targetAbsentFillerId  = _np.array(targetAbsentFillerId)
        targetAbsentRejectId  = _np.array(targetAbsentRejectId)
        targetAbsentSuspectId = _np.array(targetAbsentSuspectId)

        targetPresentFillerId  = _np.array(targetPresentFillerId)
        targetPresentRejectId  = _np.array(targetPresentRejectId)
        targetPresentSuspectId = _np.array(targetPresentSuspectId)

        clHigh = cl 
        clLow  = 100-clHigh

        cac_low                     = _np.percentile(cac,clLow,axis=0)
        cac_high                    = _np.percentile(cac,clHigh,axis=0)

        targetAbsentFillerId_low  = _np.percentile(targetAbsentFillerId,clLow,axis=0)
        targetAbsentFillerId_high = _np.percentile(targetAbsentFillerId,clHigh,axis=0)

        targetAbsentRejectId_low  = _np.percentile(targetAbsentRejectId,clLow,axis=0)
        targetAbsentRejectId_high = _np.percentile(targetAbsentRejectId,clHigh,axis=0)

        targetAbsentSuspectId_low  = _np.percentile(targetAbsentSuspectId,clLow,axis=0)
        targetAbsentSuspectId_high = _np.percentile(targetAbsentSuspectId,clHigh,axis=0)  

        targetPresentFillerId_low  = _np.percentile(targetPresentFillerId,clLow,axis=0)
        targetPresentFillerId_high = _np.percentile(targetPresentFillerId,clHigh,axis=0)

        targetPresentRejectId_low  = _np.percentile(targetPresentRejectId,clLow,axis=0)
        targetPresentRejectId_high = _np.percentile(targetPresentRejectId,clHigh,axis=0)

        targetPresentSuspectId_low  = _np.percentile(targetPresentSuspectId,clLow,axis=0)
        targetPresentSuspectId_high = _np.percentile(targetPresentSuspectId,clHigh,axis=0)        

        template = self.data_rates.loc['cac','central']
        self.data_rates = self.data_rates.append(_pandas.Series(cac_low, name = ('cac','low'), index = template.index))
        self.data_rates = self.data_rates.append(_pandas.Series(cac_high, name = ('cac','high'), index = template.index))

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

    def plotROC(self, label = "ROC", relativeFrequencyScale = 400) :
        x = _np.linspace(0,1,100)

        _plt.plot(x,x,"--",color="black",linewidth=1.0)
        _plt.scatter(self.data_rates.loc['targetAbsent', 'suspectId'],
                     self.data_rates.loc['targetPresent','suspectId'],
                     s = self.data_rates.loc['rf','']*relativeFrequencyScale,
                     label = label)
        
        # Plot errors if they have been calculated
        try : 
            _plt.errorbar(self.data_rates.loc['targetAbsent', 'suspectId'],
                          self.data_rates.loc['targetPresent','suspectId'],
                          xerr = [self.data_rates.loc['targetAbsent', 'suspectId'] - self.data_rates.loc['targetAbsent', 'suspectId_low'],
                                  self.data_rates.loc['targetAbsent', 'suspectId_high'] - self.data_rates.loc['targetAbsent', 'suspectId']],                        
                          yerr = [self.data_rates.loc['targetPresent','suspectId'] - self.data_rates.loc['targetPresent','suspectId_low'],
                                  self.data_rates.loc['targetPresent','suspectId_high']- self.data_rates.loc['targetPresent','suspectId']])
        except KeyError :
            pass
         

        _plt.xlabel("False ID rate")
        _plt.ylabel("Correct ID rate")
        


        
        # Tight layout for plot
        _plt.tight_layout()

    def plotCAC(self, label = "CAC", relativeFrequencyScale = 400) :
         _plt.scatter(self.data_rates.columns.get_level_values('confidence'),
                      self.data_rates.loc['cac','central'],
                      s = self.data_rates.loc['rf','']*relativeFrequencyScale,
                      label = label)        

         # Plot errors if they have been calculated
         try : 
             _plt.errorbar(self.data_rates.columns.get_level_values('confidence'),
                           self.data_rates.loc['cac','central'],
                           yerr = [self.data_rates.loc['cac','central']-self.data_rates.loc['cac','low'],
                                   self.data_rates.loc['cac','high']-self.data_rates.loc['cac','central']])
         except KeyError :
             pass

         _plt.xlabel("Confidence")
         _plt.ylabel("Proportion correct") 

         if self.reverseConfidence :
             ax = _plt.gca()
             lx = ax.get_xlim()
             ax.set_xlim([lx[1],lx[0]])

         # Tight layout for plot
         _plt.tight_layout()

    def plotRAC(self) : 
        pass

    def printPivot(self) :
        print(self.data_pivot)

    def printRates(self) :
        print(self.data_rates)

    def numberConditions(self) :
        return self.data_rates.columns.get_level_values('confidence').size

    def writeRatesCsv(self, fileName) : 
        self.data_rates.to_csv(fileName)

    def writeRatesExcel(self, fileName) : 
        self.data_rates.to_excel(fileName, engine = 'openpyxl')        

    def writePivotCsv(self, fileName) : 
        self.data_pivot.to_csv(fileName)

    def writePivotSimpleCsv(self, fileNameStub) : 
        pass

    def writePivotExcel(self, fileName, engine = 'openpyxl') :
        self.data_pivot.to_excel(fileName)


        
    
