import matplotlib.pyplot as _plt
import numpy as _np

class DataProcessed :
    def __init__(self, data_pivot, reverseConfidence = False, lineupSize = 1) : 
        self.data_pivot        = data_pivot 
        self.lineupSize        = lineupSize 
        self.reverseConfidence = reverseConfidence
        self.numberTPLineups   = data_pivot.loc['targetPresent'].sum().sum()
        self.numberTALineups   = data_pivot.loc['targetAbsent'].sum().sum()
        self.calculateRates(reverseConfidence)
        self.calculateRelativeFrequency()
        self.calculateCAC()

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
        cac.name = ("cac","")
        self.data_rates = self.data_rates.append(cac)
        self.data_rates = self.data_rates.sort_index()      

    def plotROC(self, label = "ROC", relativeFrequencyScale = 400) :
        x = _np.linspace(0,1,100)

        _plt.plot(x,x,"--",color="black",linewidth=1.0)
        _plt.scatter(self.data_rates.loc['targetAbsent', 'suspectId'],
                     self.data_rates.loc['targetPresent','suspectId'],
                     s = self.data_rates.loc['rf','']*relativeFrequencyScale,
                     label = label)
        _plt.xlabel("False ID rate")
        _plt.ylabel("Corred ID rate")
        

    def plotCAC(self, label = "CAC", relativeFrequencyScale = 400) :
         _plt.scatter(self.data_rates.columns.get_level_values('confidence'),
                      self.data_rates.loc['cac',''],
                      s = self.data_rates.loc['rf','']*relativeFrequencyScale,
                      label = label)        
         _plt.xlabel("Confidence")
         _plt.ylabel("Proportion correct") 

         if self.reverseConfidence :
             ax = _plt.gca()
             lx = ax.get_xlim()
             ax.set_xlim([lx[1],lx[0]])

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
        self.data_rates.to_excel(fileName)        

    def writePivotCsv(self, fileName) : 
        self.data_pivot.to_csv(fileName)

    def writePivotSimpleCsv(self, fileNameStub) : 
        pass

    def writePivotExcel(self, fileName) :
        self.data_pivot.to_excel(fileName)


        
    
