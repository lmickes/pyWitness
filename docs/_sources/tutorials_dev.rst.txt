Developer tutorials
===================

Making a new likelihood  model
------------------------------

.. code-block :: python
   :linenos:
   :emphasize-lines: 9, 15, 22-26, 33-38, 44-48

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
                       self.sigma(x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize)))

            def probTargetIDTargetPresentIntegral(x1, x2):
                return _integrate.quad(probTargetIDTargetPresent, x1, x2)[0]

            # filler ID in target present lineups
            def probFillerIDTargetPresent(x):
                return normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-2)*\
                       normpdf(x,self.lureMean.value, self.lureSigma.value)*\
                       normcdf(x,self.targetMean.value, self.targetSigma.value)*\
                       (1-normcdf(float(c),
                       self.mean( x,self.lureMean.value, self.lureSigma.value,self.targetMean.value,self.targetSigma.value,self.lineupSize),
                       self.sigma(x,self.lureMean.value, self.lureSigma.value,self.targetMean.value,self.targetSigma.value,self.lineupSize)))

            def probFillerIDTargetPresentIntegral(x1, x2):
                return _integrate.quad(probFillerIDTargetPresent, x1, x2)[0]

            def probFillerIDTargetAbsent(x):
                return normpdf(x,self.lureMean.value,self.lureSigma.value)*\
                       normcdf(x,self.lureMean.value, self.lureSigma.value)**(self.lineupSize-1)*\
                       (1-normcdf(float(c),
                       self.mean( x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize),
                       self.sigma(x,self.lureMean.value, self.lureSigma.value,self.lureMean.value,self.lureSigma.value,self.lineupSize))

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

Making a new Monte Carlo decision rule
--------------------------------------

Running tests
-------------

Interfacing R code
------------------

Interfacing Matlab code
-----------------------

Running the test suite
----------------------

Making the logo
---------------

.. code-block:: python

    import pyWitness
    dr = pyWitness.DataRaw("./test1.csv")
    dp = dr.process()
    dp.calculateConfidenceBootstrap(nBootstraps=80,plotROC=True)

