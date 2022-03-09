import pyWitness

import matplotlib.pyplot as  _plt

mplc1 = "#1f77b4"
mplc2 = "#ff7f0e"
mplc3 = "#2ca02c"
mplc4 = "#d62728"
mplc5 = "#9467bd"
mplc6 = "#8c564b"

def pAUCexample() : 
	dr = pyWitness.DataRaw("test2.csv")
	dr.cutData(column="previouslyViewedVideo",value=1,option="keep")
	dpControl = dr.process(column="group", condition="Control")
	dpVerbal = dr.process(column="group", condition="Verbal")
	minRate = min(dpControl.liberalTargetAbsentSuspectId,dpVerbal.liberalTargetAbsentSuspectId)
	dpControl = dr.process("group","Control",pAUCLiberal=minRate)
	dpControl.calculateConfidenceBootstrap(nBootstraps=2000)
	dpVerbal = dr.process("group","Verbal",pAUCLiberal=minRate)
	dpVerbal.calculateConfidenceBootstrap(nBootstraps=2000)
	dpControl.comparePAUC(dpVerbal)
	dpControl.plotROC(label = "Control data", relativeFrequencyScale=400, color = mplc1)
	dpVerbal.plotROC(label = "Verbal data", relativeFrequencyScale=400, color = mplc5)
	mfControl = pyWitness.ModelFitIndependentObservation(dpControl)
	mfControl.setEqualVariance()
	mfControl.setParameterEstimates()
	mfControl.fit()
	mfVerbal = pyWitness.ModelFitIndependentObservation(dpVerbal)
	mfVerbal.setEqualVariance()
	mfVerbal.setParameterEstimates()
	mfVerbal.fit()
	mfControl.plotROC(label = "Control IO EV",colorFromLabel="Control data")
	mfVerbal.plotROC(label = "Verbal IO EV",colorFromLabel="Verbal data")
	_plt.xlim(0,0.16)
	_plt.ylim(0,1.0)
	_plt.tight_layout()
	_plt.legend(loc=2)
	_plt.savefig("test2ROCs.pdf")