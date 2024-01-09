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

        assert len(dr.data) == 890, "test_tutorialCode1 wrong number of participants"

    def test_tutorialCode2(self) :
        import pyWitness    
        dr = pyWitness.DataRaw("test1.csv")
        dr.checkData()

    def test_tutorialCode3(self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.columnValues("responseTime")

    def test_tutorialCode3_1(self):
        import pyWitness
        dr = pyWitness.DataRaw("test1.xlsx","test1")

    def test_tutorialCode4 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()

        assert dp.data_pivot.loc[("targetAbsent","fillerId"),("confidence",0)] == 2, "test_tutorialCode4 wrong targetAbsent fillerId confidence 0"
        assert dp.data_pivot.loc[("targetPresent","fillerId"),("confidence",80)] == 5, "test_tutorialCode4 wrong targetPresent fillerId confidence 80"
        assert dp.data_rates.loc[("dprime","central"),("confidence",0)] == 1.9752208100241062, "test_tutorialCode4 wrong dprime central confidence 0"
        assert dp.data_rates.loc[("rf",""),("confidence",0)] == 0.007829977628635347, "test_tutorialCode4 wrong rf confidence 0"
        assert dp.data_rates.loc[("targetAbsent","fillerId"),("confidence",0)] == 0.28442437923250563, "test_tutorialCode4 wrong targetAbsent fillerId confidence 0"
        assert dp.data_rates.loc[("targetAbsent","rejectId"),("confidence",0)] == 0.7155756207674944, "test_tutorialCode4 wrong targetAbsent rejectId confidence 0"
        assert dp.data_rates.loc[("targetPresent","fillerId"),("confidence",0)] == 0.09395973154362416, "test_tutorialCode4 wrong targetPresent fillerId confidence 0"
        assert dp.data_rates.loc[("targetPresent","rejectId"),("confidence",0)] == 0.28635346756152125, "test_tutorialCode4 wrong targetPresent rejectId confidence 0"
        assert dp.data_rates.loc[("targetPresent","suspectId"),("confidence",0)] == 0.6196868008948546, "test_tutorialCode4 wrong targetPresent suspectId confidence 0"
        assert dp.data_rates.loc[("zL","central"),("confidence",0)] == -1.6705624914099477, "test_tutorialCode4 wrong zL central confidence 0"
        assert dp.data_rates.loc[("zT","central"),("confidence",0)] == 0.3046583186141586, "test_tutorialCode4 wrong zT central confidence 0"

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

    def test_tutorialCode8dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                                     bins=[0, 5000, 10000, 15000, 20000, 99999],
                                     labels=[1, 2, 3, 4, 5])

        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        _plt.figure(1)
        dpRAC.plotROC()
        _plt.figure(2)
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

        #stew? categorical? i didn't do resopnse time - though you can group into categories

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

    def test_tutorialCode11dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                            bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])

        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dpRAC.plotROC()

    def test_tutorialCode12 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        print(dp.pAUC)

        assert dp.pAUC == 0.020750138845233933, "test_tutorialCode12 wrong pAUC"   

    def test_tutorialCode12dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                            bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])

        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        print(dpRAC.pAUC)

    def test_tutorialCode13 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.setParameterEstimates()
        mf.fit()
        mf.printParameters()

    def test_tutorialCode13dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                            bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])

        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        
        #messy!

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

    def test_tutorialCode14dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                            bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])

        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        mfRAC.printParameters()

    def test_tutorialCode15 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column="confidence")
        dp = dr.process()

        mf_io = pyWitness.ModelFitIndependentObservation(dp)
        mf_br = pyWitness.ModelFitBestRest(dp)
        mf_en = pyWitness.ModelFitEnsemble(dp)
        mf_in = pyWitness.ModelFitIntegration(dp)

    def test_tutorialCode15dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])

        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        mfRAC_io = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC_br = pyWitness.ModelFitBestRest(dpRAC)
        mfRAC_en = pyWitness.ModelFitEnsemble(dpRAC)
        mfRAC_in = pyWitness.ModelFitIntegration(dpRAC)

    def test_tutorialCode16 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= [1,2,3])
        dp = dr.process()
        dp.plotHitVsFalseAlarmRate()
        
    def test_tutorialCode16dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dpRAC.plotHitVsFalseAlarmRate()

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

        assert mf.targetMean.value == 1.7976601843420954, "test_tutorialCode17 wrong mf targetMean"
        #assert targetBetweenSigma ==

    def test_tutorialCode17dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.printParameters()

        mfRAC.setEqualVariance()
        mfRAC.setParameterEstimates()
        mfRAC.printParameters()

        mfRAC.fit()
        mfRAC.printParameters()

    def test_tutorialCode18 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()

    def test_tutorialCode18dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dpRAC.calculateConfidenceBootstrap(nBootstraps=200)
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()

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

    def test_tutorialCode19dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                    bins=[0, 5000, 10000, 15000, 20000, 99999],
                            labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")

        dpRAC.calculateConfidenceBootstrap(nBootstraps=200)
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        #new code
        dpRAC.plotROC(label="Data")
        mfRAC.plotROC(label="Indep. obs. fit")
        
    def test_tutorialCode20 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels= None)
        dp = dr.process()
        dp.calculateConfidenceBootstrap(nBootstraps=200)
        mf = pyWitness.ModelFitIndependentObservation(dp)
        mf.setEqualVariance()
        mf.fit()

        assert mf.pValue == 0.035660197825222784, "test_tutorialCode20 wrong mf p-value"
        assert mf.d == 1.7976601843420954, "test_tutorialCode20 wrong mf d"
        assert mf.c1.value == 1.4017022884785224, "test_tutorialCode20 wrong mf c1"
        assert mf.c2.value == 1.93548009449426, "test_tutorialCode20 wrong mf c2"
        assert mf.c3.value == 1.93548009449426, "test_tutorialCode20 wrong mf c3"

 
        dp.plotROC(label="Data")
        mf.plotROC(label="Indep. obs. fit")

        import matplotlib.pyplot as _plt
        _plt.legend()        
        #new code
        dp.plotCAC(label="Data")
        mf.plotCAC(label="Indep. obs. fit")

        import matplotlib.pyplot as _plt
        _plt.legend()

    def test_tutorialCode20dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime") 
        dpRAC.calculateConfidenceBootstrap(nBootstraps=200)
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        dpRAC.plotROC(label="Data")
        mfRAC.plotROC(label="Indep. obs. fit")
        import matplotlib.pyplot as _plt
        _plt.legend()        
        #new code
        dpRAC.plotCAC(label="Data")
        mfRAC.plotCAC(label="Indep. obs. fit")

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
        
    def test_tutorialCode20adv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime") 
        dpRAC.calculateConfidenceBootstrap(nBootstraps=200)
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        #new code
        mfRAC.plotFit()

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

    def test_tutorialCode21dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dpRAC.calculateConfidenceBootstrap(nBootstraps=200)
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        #new code
        mfRAC.plotModel()

    def test_tutorialCode22 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dp = dr.process()
        dp.writePivotExcel("test1_pivot.xlsx")
        dp.writePivotCsv("test1_pivot.csv")
        dp.writeRatesExcel("test1_rates.xlsx")
        dp.writeRatesCsv("test1_rates.csv")

    def test_tutorialCode22dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dpRAC.writePivotExcel("test1_pivot.xlsx")
        dpRAC.writePivotCsv("test1_pivot.csv")
        dpRAC.writeRatesExcel("test1_rates.xlsx")
        dpRAC.writeRatesCsv("test1_rates.csv")

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
    
    def test_tutorialCode27dv (self) :
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

    def test_tutorialCode31dv (self) :
        import pyWitness
        dr1RAC = pyWitness.DataRaw("test1.csv")
        dr2RAC = pyWitness.DataRaw("test1.csv")
        dr1RAC.collapseContinuousData(column="responseTime",
                        bins=[0, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4])
        dr2RAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dp1RAC = dr1RAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dp2RAC = dr2RAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dp1RAC.calculateConfidenceBootstrap(nBootstraps=200)
        dp2RAC.calculateConfidenceBootstrap(nBootstraps=200)
        dp1RAC.plotCAC()
        dp2RAC.plotCAC()

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

    def test_tutorialCode32dv (self) :
        import pyWitness
        dr1RAC = pyWitness.DataRaw("test1.csv")
        dr2RAC = pyWitness.DataRaw("test1.csv")
        dr1RAC.collapseContinuousData(column="responseTime",
                        bins=[0, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4])
        dr2RAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])

        dp1RAC = dr1RAC.process(reverseConfidence=True, dependentVariable="responseTime")
        dp2RAC = dr2RAC.process(reverseConfidence=True, dependentVariable="responseTime")

        dp1RAC.plotCAC(label = "4 bins")
        dp2RAC.plotCAC(label = "5 bins")

        import matplotlib.pyplot as _plt
        _plt.legend()

        xlim(0,50000)
        ylim(0.50,1.0)

    def test_tutorialCode33 (self) :
        import pyWitness
        dr = pyWitness.DataRaw("test1.csv")
        dr.collapseContinuousData(column = "confidence",bins = [-1,60,80,100],labels=None)
        dp = dr.process()
        mf = pyWitness.ModelFitIndependentObservation(dp, debug=True)
        mf.setEqualVariance()
        mf.fit()
        dr1 = mf.generateRawData(nGenParticipants=10000)

    def test_tutorialCode33dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC, debug=True)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        dr1RAC = mfRAC.generateRawData(nGenParticipants=10000)

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
 
    def test_tutorialCode34dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC, debug=True)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        dr1RAC = mfRAC.generateRawData(nGenParticipants=10000)
        #new code
        dr1RAC.writeCsv("fileNameRAC.csv")
        dr1RAC.writeExcel("fileNameRAC.xlsx")

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

    def test_tutorialCode35dv (self) :
        import pyWitness
        drRAC = pyWitness.DataRaw("test1.csv")
        drRAC.collapseContinuousData(column="responseTime",
                        bins=[0, 5000, 10000, 15000, 20000, 99999],
                                labels=[1, 2, 3, 4, 5])
        dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
        mfRAC = pyWitness.ModelFitIndependentObservation(dpRAC, debug=True)
        mfRAC.setEqualVariance()
        mfRAC.fit()
        dr1RAC = mfRAC.generateRawData(nGenParticipants=10000)
        #new code
        # Need to process the synthetic data
        dp1RAC = dr1RAC.process()

        # calculate uncertainties using bootstrap
        dpRAC.calculateConfidenceBootstrap()
        dp1RAC.calculateConfidenceBootstrap()

        # plot ROCs
        dpRAC.plotROC(label="Experimental data")
        dp1RAC.plotROC(label="Simulated data")
        mfRAC.plotROC(label="Model fit")

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