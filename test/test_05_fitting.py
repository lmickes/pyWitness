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
    dr.collapseContinuousData(column="confidence", bins=[-1, 40, 60, 80, 100], labels=[1, 2, 3, 4])
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

def test_05_fitting_test1_csv_best_rest_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf = pyWitness.ModelFitBestRest(dp)
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(23.203557131914106, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(5.800889282978527, rel=1e-5)
    assert mf.pValue == pytest.approx(0.00011530375016544081, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.03566192879208, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(-0.027650790308206018, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(-0.027650790308206018, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.7353510716101122, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.212736570519106, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.9491721140631633, rel=1e-5)

def test_05_fitting_test1_csv_best_rest_uneqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf = pyWitness.ModelFitBestRest(dp)
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(7.868684226378687, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 3
    assert mf.chi2PerNDF == pytest.approx(2.622894742126229, rel=1e-5)
    assert mf.pValue == pytest.approx(0.04880501500208234, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.038036936738798, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.6139740611429738, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.03895753863353904, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.03895753863353904, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.7546932765997934, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.168399339678346, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.7606531061053246, rel=1e-5)

def test_05_fitting_test1_csv_best_rest_free():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 40, 60, 80, 100], labels=[1, 2, 3, 4])
    dp = dr.process()
    mf = pyWitness.ModelFitBestRest(dp)
    mf.fit()

    assert mf.chi2 == pytest.approx(9.92916150379401, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 2
    assert mf.chi2PerNDF == pytest.approx(4.964580751897005, rel=1e-5)
    assert mf.pValue == pytest.approx(0.006980876815037118, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0018987441970468675, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(0.6861322853955167, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.4012317220792951, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.4268722771827042, rel=1e-5)
    #assert mf.lureBetweenSigma.value == pytest.approx(0.00035201600917691706, abs=0.001)
    #assert mf.targetBetweenSigma.value == pytest.approx(0.0008327066039283845, abs=0.001)
    assert mf.c1.value == pytest.approx(1.2028664376190874, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.29788822134375, rel=1e-5)
    assert mf.c3.value == pytest.approx(1.4905841431052758, rel=1e-5)

def test_05_fitting_test1_csv_ensemble_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf = pyWitness.ModelFitEnsemble(dp)
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(23.20355799888823, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(5.800889499722057, rel=1e-5)
    assert mf.pValue == pytest.approx(0.00011530370414902791, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.03564527876075, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.0025862757713492144, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.0025862757713492144, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.4461421641934356, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.8439293779396513, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.457635059181422, rel=1e-5)

def test_05_fitting_test1_csv_ensemble_uneqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf = pyWitness.ModelFitEnsemble(dp)
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(7.868684371812639, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 3
    assert mf.chi2PerNDF == pytest.approx(2.6228947906042133, rel=1e-5)
    assert mf.pValue == pytest.approx(0.04880501181888286, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.0380474980579812, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.6139499862139856, rel=1e-3)
    #assert mf.lureBetweenSigma.value == pytest.approx(-0.045359525568252, rel=1e-5)
    #assert mf.targetBetweenSigma.value == pytest.approx(-0.045359525568252, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.4622645372725116, rel=2e-5)
    assert mf.c2.value == pytest.approx(1.807018272986906, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.3005632098784905, rel=1e-5)

def test_05_fitting_test1_csv_ensemble_free():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 40, 60, 80, 100], labels=[1, 2, 3, 4])
    dp = dr.process()
    mf = pyWitness.ModelFitEnsemble(dp)
    mf.fit()

    assert mf.chi2 == pytest.approx(9.929160528690728, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 2
    assert mf.chi2PerNDF == pytest.approx(4.964580264345364, rel=1e-5)
    assert mf.pValue == pytest.approx(0.006980880218575902, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(-0.00019209760974083547, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(0.7574113379383993, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.5445278559161522, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.4712095135660104, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.0047163119561311004, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(-0.0007144208090970518, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.106509748503039, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.193916803861908, rel=1e-5)
    assert mf.c3.value == pytest.approx(1.371185767314882, rel=1e-5)
    assert mf.c4.value == pytest.approx(1.7468725897881834, rel=1e-5)

def test_05_fitting_test1_csv_integration_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf = pyWitness.ModelFitIntegration(dp)
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(12.782436722859641, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(3.1956091807149103, rel=1e-5)
    assert mf.pValue == pytest.approx(0.012389254262285876, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.5366281782007007, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(5.115694387174446e-05, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(5.115694387174446e-05, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.2251095944199202, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.764720963085291, rel=1e-5)
    assert mf.c3.value == pytest.approx(4.786453224625339, rel=1e-5)

def test_05_fitting_test1_csv_integration_uneqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf = pyWitness.ModelFitIntegration(dp)
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(7.346304597247939, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 3
    assert mf.chi2PerNDF == pytest.approx(2.448768199082646, rel=1e-5)
    assert mf.pValue == pytest.approx(0.06164187352643058, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.734951478496513, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.4440682177718327, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(4.567067698853903e-05, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(4.567067698853903e-05, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.281468457077398, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.900821480460631, rel=1e-5)
    assert mf.c3.value == pytest.approx(5.06921554942873, rel=1e-5)

def test_05_fitting_test1_csv_integration_free():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 40, 60, 80, 100], labels=[1, 2, 3, 4])
    dp = dr.process()
    mf = pyWitness.ModelFitIntegration(dp)
    mf.fit()

    assert mf.chi2 == pytest.approx(10.222524151352737, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 2
    assert mf.chi2PerNDF == pytest.approx(5.111262075676368, rel=1e-5)
    assert mf.pValue == pytest.approx(0.006028469735381514, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(-0.0007710566698620955, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(0.5920046766071095, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.6250990449599445, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.8877215913533945, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(-0.000838028225441163, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.0004049627542837209, rel=1e-5)
    assert mf.c1.value == pytest.approx(0.7498003652968959, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.079274299875618, rel=1e-5)
    assert mf.c3.value == pytest.approx(1.7237076691036173, rel=1e-5)
    assert mf.c4.value == pytest.approx(3.0151183915768636, rel=1e-5)

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

def test_05_fitting_test3_csv_indep_obs_eqvar() :
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dr.collapseContinuousData(column="confidence", bins=[-12, -9.5, -7.5, 0, 7.5, 9.5, 12.5], labels=[1, 2, 3, 4, 5, 6])

    dp = dr.process()

    mf = pyWitness.ModelFitIndependentObservation(dp, debug=False)
    mf.setParameterEstimates()
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(6.23202615170196, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 5
    assert mf.chi2PerNDF == pytest.approx(1.2464052303403919, rel=1e-5)
    assert mf.pValue == pytest.approx(0.2842920239676301, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(0.9265913547430601, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.27049445313722853, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.27049445313722853, rel=1e-5)
    assert mf.c1.value == pytest.approx(-10.0, rel=1e-5)
    assert mf.c2.value == pytest.approx(-0.49984935445356177, rel=1e-5)
    assert mf.c3.value == pytest.approx(0.1573676648728698, rel=1e-5)
    assert mf.c4.value == pytest.approx(0.6775665751531148, rel=1e-5)
    assert mf.c5.value == pytest.approx(1.0251682838468397, rel=1e-5)
    assert mf.c6.value == pytest.approx(1.82886097851483, rel=1e-5)

def test_05_fitting_test3_csv_indep_obs_uneqvar() :
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dr.collapseContinuousData(column="confidence", bins=[-12, -9.5, -7.5, 0, 7.5, 9.5, 12.5], labels=[1, 2, 3, 4, 5, 6])

    dp = dr.process()

    mf = pyWitness.ModelFitIndependentObservation(dp, debug=False)
    mf.setParameterEstimates()
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(5.806361946665044, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(1.451590486666261, rel=1e-5)
    assert mf.pValue == pytest.approx(0.21408350742647464, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(0.9133315407094696, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.965437881652407, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.31649901012369414, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.31649901012369414, rel=1e-5)
    assert mf.c1.value == pytest.approx(-10.0, rel=1e-5)
    assert mf.c2.value == pytest.approx(-0.4875453897532963, rel=1e-5)
    assert mf.c3.value == pytest.approx(0.16227837347944246, rel=1e-5)
    assert mf.c4.value == pytest.approx(0.6739989618052868, rel=1e-5)
    assert mf.c5.value == pytest.approx(1.0140686368186151, rel=1e-5)
    assert mf.c6.value == pytest.approx(1.798517051043007, rel=1e-5)

def test_05_fitting_test1ds_csv_indep_obs_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1ds.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitDesignatedInnocentIndependentObservationSimple(dp)
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(18.204401916765956, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 5
    assert mf.chi2PerNDF == pytest.approx(3.640880383353191, rel=1e-5)
    assert mf.pValue == pytest.approx(0.0027008455417510957, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.9787441631738854, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.09022800640627925, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.09022800640627925, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.6491349104953958, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.1341156336168696, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.830997744233964, rel=1e-5)
    assert mf.innocentMean.value == pytest.approx(0.07628384576911576, rel=1e-5)
    assert mf.innocentSigma.value == pytest.approx(1.0879386396514419, rel=1e-5)

def test_05_fitting_test1ds_csv_indep_obs_uneqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1ds.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitDesignatedInnocentIndependentObservationSimple(dp)
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(6.7970858525318105, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(1.6992714631329526, rel=1e-5)
    assert mf.pValue == pytest.approx(0.14700780574509875, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(1.9907450134230142, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.7332110669123757, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(-0.11280393013592838, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(-0.11280393013592838, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.6871967806020884, rel=1e-5)
    assert mf.c2.value == pytest.approx(2.1091411453906987, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.6862139553409516, rel=1e-5)
    assert mf.innocentMean.value == pytest.approx(0.344896655015678, rel=1e-5)
    assert mf.innocentSigma.value == pytest.approx(0.9282807867028133, rel=1e-5)

def test_05_fitting_test1ds_csv_ensemble_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1ds.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitDesignatedInnocentEnsemble(dp)
    mf.setEqualVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(35.51581638810221, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 5
    assert mf.chi2PerNDF == pytest.approx(7.103163277620442, rel=1e-5)
    assert mf.pValue == pytest.approx(1.1869540919029475e-06, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.0974060361264386, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(-0.031142266590266764, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(-0.031142266590266764, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.506989255053122, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.8951853445369462, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.5025505327703743, rel=1e-5)
    assert mf.innocentMean.value == pytest.approx(0.05457675538293864, rel=1e-5)
    assert mf.innocentSigma.value == pytest.approx(1.060250215704164, rel=1e-5)

def test_05_fitting_test1ds_csv_ensemble_uneqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1ds.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitDesignatedInnocentEnsemble(dp)
    mf.setUnequalVariance()
    mf.fit()

    assert mf.chi2 == pytest.approx(18.016979543009537, rel=1e-5)
    assert mf.numberDegreesOfFreedom == 4
    assert mf.chi2PerNDF == pytest.approx(4.504244885752384, rel=1e-5)
    assert mf.pValue == pytest.approx(0.0012247040432307177, rel=1e-5)
    assert mf.lureMean.value == pytest.approx(0.0, rel=1e-5)
    assert mf.lureSigma.value == pytest.approx(1.0, rel=1e-5)
    assert mf.targetMean.value == pytest.approx(2.094412333476179, rel=1e-5)
    assert mf.targetSigma.value == pytest.approx(0.5698452640288771, rel=1e-5)
    assert mf.lureBetweenSigma.value == pytest.approx(0.06993018541520893, rel=1e-5)
    assert mf.targetBetweenSigma.value == pytest.approx(0.06993018541520893, rel=1e-5)
    assert mf.c1.value == pytest.approx(1.5255021006908551, rel=1e-5)
    assert mf.c2.value == pytest.approx(1.8498785927802304, rel=1e-5)
    assert mf.c3.value == pytest.approx(2.3206657594929387, rel=1e-5)
    assert mf.innocentMean.value == pytest.approx(0.41199044902032644, rel=1e-5)
    assert mf.innocentSigma.value == pytest.approx(0.821344641932431, rel=1e-5)

