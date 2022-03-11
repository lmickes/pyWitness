import pyWitness 
import matplotlib.pyplot as _plt

mplc1 = "#1f77b4"
mplc2 = "#ff7f0e"
mplc3 = "#2ca02c"
mplc4 = "#d62728"
mplc5 = "#9467bd"
mplc6 = "#8c564b"

def showup() :
	dr = pyWitness.DataRaw("./test3.csv")
	dr.collapseContinuousData(bins=[-11.5,-10.5,-9.5,-8.5,-7.5,-6.5,-5.5,-4.5,-3.5,
									-2.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5],
									labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
	dp = dr.process()
	dp.calculateConfidenceBootstrap(nBootstraps=200)
	mf = pyWitness.ModelFitIndependentObservationSimple(dp)
	mf.setEqualVariance()
	mf.setParameterEstimates()
	mf.debug = True 
	mf.targetMean.value = 0.911
	mf.targetBetweenSigma.value = 0.0
	mf.targetBetweenSigma.fixed = True
	mf.c1.value  = -10.000
	mf.c1.fixed  = True
	mf.c2.value  = -0.708
	mf.c3.value  = -0.510
	mf.c4.value  = -0.207
	mf.c5.value  =  0.144 
	mf.c6.value  =  0.361
	mf.c7.value  =  0.498
	mf.c8.value  =  0.579
	mf.c9.value  =  0.627
	mf.c10.value =  0.649
	mf.c11.value =  0.676
	mf.c12.value =  0.681
	mf.c13.value =  0.697
	mf.c14.value =  0.742
	mf.c15.value =  0.831
	mf.c16.value =  1.018 
	mf.c17.value =  1.397
	mf.c18.value =  1.819
	mf.c19.value =  2.190	
	mf.fit()

	dp.plotROC(label="test3 data",color=mplc3)
	mf.plotROC(label="IO EV fit",colorFromLabel="test3 data")
	_plt.savefig("test3ROC.pdf")
	_plt.legend(loc=4)

#ModelFit.printParameters>  lureMean 0.000 (fixed)
#ModelFit.printParameters>  lureSigma 1.000 (fixed targetSigma)
#ModelFit.printParameters>  targetMean 0.911 (free)
#ModelFit.printParameters>  targetSigma 1.000 (fixed)
#ModelFit.printParameters>  lureBetweenSigma -0.007 (fixed targetBetweenSigma)
#ModelFit.printParameters>  targetBetweenSigma -0.007 (free)
#ModelFit.printParameters>  c1 -10.000 (fixed)
#ModelFit.printParameters>  c2 -0.708 (free)
#ModelFit.printParameters>  c3 -0.510 (free)
#ModelFit.printParameters>  c4 -0.207 (free)
#ModelFit.printParameters>  c5 0.144 (free)
#ModelFit.printParameters>  c6 0.361 (free)
#ModelFit.printParameters>  c7 0.498 (free)
#ModelFit.printParameters>  c8 0.579 (free)
#ModelFit.printParameters>  c9 0.627 (free)
#ModelFit.printParameters>  c10 0.649 (free)
#ModelFit.printParameters>  c11 0.676 (free)
#ModelFit.printParameters>  c12 0.681 (free)
#ModelFit.printParameters>  c13 0.697 (free)
#ModelFit.printParameters>  c14 0.742 (free)
#ModelFit.printParameters>  c15 0.831 (free)
#ModelFit.printParameters>  c16 1.018 (free)
#ModelFit.printParameters>  c17 1.397 (free)
#ModelFit.printParameters>  c18 1.819 (free)
#ModelFit.printParameters>  c19 2.190 (free)
