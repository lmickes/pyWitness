import pyWitness
import matplotlib.pyplot as _plt

class UnitTests :
    def test1DataNormal(self,fileName = "test1.csv") :
        pass


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
