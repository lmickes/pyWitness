import matplotlib.pyplot as _plt
import numpy as _np

class DataProcessed :
    def __init__(self, data_pivot, reverseConfidence = False, lineupSize = 1) : 
        self.data_pivot = data_pivot 
        self.calculateRates(reverseConfidence)
        self.lineupSize = lineupSize 

    def calculateRates(self, reverseConfidence = False) :
        self.data_rates = self.data_pivot.copy()

        # reverse confidence
        self.reverseConfidence = reverseConfidence
        if not reverseConfidence : 
            columns = self.data_rates.columns.tolist()
            columns = columns[::-1]
            self.data_rates = self.data_rates[columns]

        self.data_rates = self.data_rates.cumsum(1)

        print(self.data_rates)

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

    def plotROC(self) :
        x = _np.linspace(0,1,100)

        _plt.plot(self.data_rates.loc['targetAbsent', 'suspectId']/self.lineupSize,
                  self.data_rates.loc['targetPresent','suspectId'],"+");
        _plt.plot(x,x,"--",color="black")
        
    def plotCAC(self) :
        pass


    def plotRAC(self) : 
        pass

    
