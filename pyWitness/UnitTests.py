import pyWitness
import matplotlib.pyplot as _plt
from matplotlib.pyplot import *
import unittest as _unittest

class UnitTests(_unittest.TestCase) :
    def test1DataNormal(self,fileName = "test1.csv") :
        pass

    def test_tutorialCode1(self) :
        import pyWitness    
        dr = pyWitness.DataRaw("test1.csv")

    def test_tutorialCode2(self) :
        import pyWitness    
        dr = pyWitness.DataRaw("test1.csv")
        dr.checkData()
   
    #Stew - this is response time; we may need to update
    def tutorialCode3(self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.columnValues("responseTime")

    def test_tutorialCode4 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()

    def test_tutorialCode5 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()
        dp.printPivot()
        dp.printRates()

    def test_tutorialCode6 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()
        dp.plotROC()

    def test_tutorialCode7 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()
        dp.plotCAC()

    def test_tutorialCode8 (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1RAC.csv")
        dpRAC = dr.process()
        dpRAC.plotCAC()

    def test_tutorialCode9 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseCategoricalData(column='confidence',
                           map={0: 30, 10: 30, 20: 30, 30: 30, 40: 30, 50: 30, 60: 30,
                                70: 75, 80: 75,
                                90: 95, 100: 95})
        dp = dr.process()
        dp.plotCAC()

    def test_tutorialCode10(self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseCategoricalData(column='confidence',
                           map={0: 30, 10: 30, 20: 30, 30: 30, 40: 30, 50: 30, 60: 30,
                                70: 75, 80: 75,
                                90: 95, 100: 95})
        dp = dr.process()
        dp.plotCAC()
        #new code
        import matplotlib as _plt
        xlim(0,100)
        ylim(0.50,1.0)

    def test_tutorialCode11 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        dp.plotROC()

    def test_tutorialCode12 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        print(dp.pAUC)

    def test_tutorialCode13 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()

    def test_tutorialCode14 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.printParameters()

        mf.setEqualVariance()
        mf.printParameters()

        mf.fit()
        mf.printParameters()

    def test_tutorialCode15 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column="confidence")
        dp = dr.process()

        mf_io = pyWitness.ModelFitIndependentObservation(dp)
        mf_br = pyWitness.ModelFitBestRest(dp)
        mf_en = pyWitness.ModelFitEnsemble(dp)
        mf_in = pyWitness.ModelFitIntegration(dp)

    def tutorialCode16 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        dp.plotHitVsFalseAlarmRate()

    def test_tutorialCode17 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.printParameters()

        mf.setEqualVariance()
        mf.setParameterEstimates()
        mf.printParameters()

        mf.fit()
        mf.printParameters()

    def test_tutorialCode18 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()

    def test_tutorialCode19 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()
        #new code
        dp.plotROC(label="Data")
        mf.plotROC(label="Indep. obs. fit")

        import matplotlib.pyplot as _plt
        _plt.legend()

    def test_tutorialCode20 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()
 
        dp.plotROC(label="Data")
        mf.plotROC(label="Indep. obs. fit")

        import matplotlib.pyplot as _plt
        _plt.legend()        
        #new code
        dp.plotCAC(label="Data")
        mf.plotCAC(label="Indep. obs. fit")

        import matplotlib.pyplot as _plt
        _plt.legend()

    def test_tutorialCode20a (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()
        #new code
        mf.plotFit()

    def test_tutorialCode21 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()
        #new code
        mf.plotModel()

    def test_tutorialCode22 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()
        dp.writePivotExcel("test1_pivot.xlsx")
        dp.writePivotCsv("test1_pivot.csv")
        dp.writeRatesExcel("test1_rates.xlsx")
        dp.writeRatesCsv("test1_rates.csv")

    #Advanced tutorial
    def test_tutorialCode23 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200, cl=95)

    def test_tutorialCode24 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test2.xlsx",excelSheet = "Sheet1")
    
    def test_tutorialCode25 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test2.csv")
        dr.cutData(column="previouslyViewedVideo",value=1,option="keep")
        dpControl = dr.process(column="group", condition="Control")
    
    def test_tutorialCode26 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test2.csv")
        dr.cutData(column="previouslyViewedVideo",value=1,option="keep")
        dpControl = dr.process(column="group", condition="Control")
        dpVerbal = dr.process(column="group", condition="Verbal")
    
    def test_tutorialCode27 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test2.csv")
        dr.cutData(column="previouslyViewedVideo",value=1,option="keep")
        dpControl = dr.process(column="group", condition="Control")
        dpVerbal = dr.process(column="group", condition="Verbal")
        minRate = min(dpControl.liberalTargetAbsentSuspectId,dpVerbal.liberalTargetAbsentSuspectId)
    
    def test_tutorialCode28 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test2.csv")
        dr.cutData(column="previouslyViewedVideo",value=1,option="keep")
        dpControl = dr.process(column="group", condition="Control")
        dpVerbal = dr.process(column="group", condition="Verbal")
        minRate = min(dpControl.liberalTargetAbsentSuspectId,dpVerbal.liberalTargetAbsentSuspectId)
        dpControl = dr.process("group","Control",pAUCLiberal=minRate)
        dpControl.calculateConfidenceBootstrap(nBootstraps=200)
        dpVerbal = dr.process("group","Verbal",pAUCLiberal=minRate)
        dpVerbal.calculateConfidenceBootstrap(nBootstraps=200)
        dpControl.comparePAUC(dpVerbal)

    def test_tutorialCode29 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test2.csv")
        dr.cutData(column="previouslyViewedVideo",value=1,option="keep")
        dpControl = dr.process(column="group", condition="Control")
        dpVerbal = dr.process(column="group", condition="Verbal")
        minRate = min(dpControl.liberalTargetAbsentSuspectId,dpVerbal.liberalTargetAbsentSuspectId)
        dpControl = dr.process("group","Control",pAUCLiberal=minRate)
        dpControl.calculateConfidenceBootstrap(nBootstraps=200)
        dpVerbal = dr.process("group","Verbal",pAUCLiberal=minRate)
        dpVerbal.calculateConfidenceBootstrap(nBootstraps=200)
        dpControl.comparePAUC(dpVerbal)
        #new code
        dpControl.plotROC(label = "Control data", relativeFrequencyScale=400)
        dpVerbal.plotROC(label = "Verbal data", relativeFrequencyScale=400)

    def test_tutorialCode30 (self) :
        import pyWitness
        dp = pyWitness.DataProcessed("test1_processed.csv", lineupSize = 6)

    def test_tutorialCode31 (self) :
        import pyWitness
        dr1 = pyWitness.DataRaw("test1.csv")
        dr2 = pyWitness.DataRaw("test1.csv")

        dr2.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels=None)

        dp1 = dr1.process()
        dp2 = dr2.process()

        dp1.plotCAC()
        dp2.plotCAC()

    def test_tutorialCode32 (self) :
        import pyWitness
        dr1 = pyWitness.DataRaw("test1.csv")
        dr2 = pyWitness.DataRaw("test1.csv")

        dr2.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels=None)

        dp1 = dr1.process()
        dp2 = dr2.process()

        dp1.plotCAC(label = "11 bins")
        dp2.plotCAC(label = "3 bins")

        import matplotlib.pyplot as _plt
        _plt.legend()

        xlim(0,100)
        ylim(0.50,1.00)

    def test_tutorialCode33 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels=None)
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp, debug=True)
        mf.setEqualVariance()
        mf.fit()
        dr1 = mf.generateRawData(nGenParticipants=10000)

    def test_tutorialCode34 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels=None)
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp, debug=True)
        mf.setEqualVariance()
        mf.fit()
        dr1 = mf.generateRawData(nGenParticipants=10000)
        #new code
        dr1.writeCsv("fileName.csv")
        dr1.writeExcel("fileName.xlsx")

    def test_tutorialCode35 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels=None)
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp, debug=True)
        mf.setEqualVariance()
        mf.fit()
        dr1 = mf.generateRawData(nGenParticipants=10000)
        #new code
        # Need to process the synthetic data
        dp1 = dr1.process()

        # calculate uncertainties using bootstrap
        dp.calculateConfidenceBootstrap()
        dp1.calculateConfidenceBootstrap()

        # plot ROCs
        dp.plotROC(label="Experimental data")
        dp1.plotROC(label="Simulated data")
        mf.plotROC(label="Model fit")

        import matplotlib.pyplot as _plt
        _plt.legend()

    '''
    def test1DataConfidence(self,fileName = "test1.csv") :
        self.dr = pyWitness.DataRaw("test1.csv")

        self.dp = self.dr.process(reverseConfidence=False, dependentVariable="confidence")

        self.dp.printPivot()
        self.dp.printRates()

        self.dp.calculateConfidenceBootstrap(200)

        _plt.figure(1)
        self.dp.plotROC()
        _plt.figure(2)
        self.dp.plotCAC()

    def test1DataResponseTime(self,fileName = "test1.csv") :
        self.dr = pyWitness.DataRaw("test1.csv")

        self.dr.collapseContinuousData(column="responseTime",
                                  bins=[0, 5000, 10000, 15000, 20000, 99999],
                                  labels=[5, 4, 3, 2, 1])

        self.dp = self.dr.process(reverseConfidence=True, dependentVariable="responseTime")

        self.dp.printPivot()
        self.dp.printRates()

        self.dp.calculateConfidenceBootstrap(200)

        _plt.figure(1)
        self.dp.plotROC()
        _plt.figure(2)
        self.dp.plotCAC()
    '''

if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore', category=FutureWarning)
    _unittest.main(verbosity=0)



    class TracingStreamResult(_testtools.StreamResult):
        def status(self, *args, **kwargs):
            print('{0[test_id]}: {0[test_status]}'.format(kwargs))