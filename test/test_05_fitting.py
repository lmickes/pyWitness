import pytest

def test_05_fitting_test1_csv_indep_obs_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(10.300411274463412, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(2.575102818615853, rel=1e-5)
    assert mf.pValue == pytest.approx(0.03566019782522267, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.7976601843420954, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.6046983921244553, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.6046983921244553, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.4017022884785224, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.93548009449426, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.677475327674742, rel=1e-5)

def test_05_fitting_test1_csv_indep_obs_uneqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(4.534824840657988, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 3
    assert mf.chi2PerNDF == pytest.approx(1.5116082802193294, rel=1e-5)
    assert mf.pValue == pytest.approx(0.20920494600886963, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.8894645402811472, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.7886365473806328, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.4480311026689192, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.4480311026689192, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.5351065745707397, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.002341182989407, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.6308524212497644, rel=1e-5)

def test_05_fitting_test1_csv_indep_obs_free():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.fit()

    assert mf.chi2 == pytest.approx(10.76520159182259, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 2
    assert mf.chi2PerNDF == pytest.approx(5.382600795911295, rel=1e-5)
    assert mf.pValue == pytest.approx(0.004595853496030644, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0006818129624015098, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(0.7613182180813651, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.493581552198572, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.5701995798268649, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(-0.0012213835415482996, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.0012586054967293737, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.25713233870699, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.3660364365503272, rel=1e-5)
    assert mf.c3.value == pytest.approx(1.5870619583040122, rel=1e-5)
    assert mf.c4.value == pytest.approx(2.033939924498857, rel=1e-5)

def test_05_fitting_test1_csv_best_rest():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf_br = pyWitness.ModelFitBestRest(dp)

def test_05_fitting_test1_csv_ensemble():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf_en = pyWitness.ModelFitEnsemble(dp)

def test_05_fitting_test1_csv_integration():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf_in = pyWitness.ModelFitIntegration(dp)

def test_05_fitting_test1_csv_set_parameters_plot_hit_v_false():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    dp.plotHitVsFalseAlarmRate()

def test_05_fitting_test1_csv_set_parameters_print_parameters():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.printParameters()

def test_05_fitting_test1_csv_set_parameters_set_equal_var():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setEqualVariance()
    mf.setParameterEstimates()
    mf.printParameters()

def test_05_fitting_test1_csv_plot_fit_roc():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
    dp = dr.process()
    dp.calculateConfidenceBootstrap(nBootstraps=200)
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setEqualVariance()
    mf.fit()
    dp.plotROC(label="Data")
    mf.plotROC(label="Indep. obs. fit")

def test_05_fitting_test1_csv_plot_fit():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
    dp = dr.process()
    dp.calculateConfidenceBootstrap(nBootstraps=200)
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setEqualVariance()
    mf.fit()
    dp.plotROC(label="Data")
    mf.plotROC(label="Indep. obs. fit")
    mf.plotFit()

def test_05_fitting_test1_csv_plot_fit_cac():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
    dp = dr.process()
    dp.calculateConfidenceBootstrap(nBootstraps=200)
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setEqualVariance()
    mf.fit()
    dp.plotCAC(label="Data")
    mf.plotCAC(label="Indep. obs. fit")