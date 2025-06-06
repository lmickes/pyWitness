import pytest

def test_adv_stats_test1_csv_bootstrap():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
    dp = dr.process()
    dp.calculateConfidenceBootstrap(nBootstraps=200, cl=95)
    dp.printPivot()
    dp.printRates()

def test_adv_stats_test3_csv_bootstrap():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dr.collapseContinuousData(column="confidence", bins=[-12, -9.5, -7.5, 0, 7.5, 9.5, 12.5], labels=[1, 2, 3, 4, 5, 6])
    dp = dr.process()
    dp.calculateConfidenceBootstrap(nBootstraps=200, cl=95)
    dp.printPivot()
    dp.printRates()

def test_adv_stats_test2_csv_processing_two_conditions():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test2.csv")
    dr.cutData(column="previouslyViewedVideo", value=1, option="keep")
    dpControl = dr.process(column="group", condition="Control")
    dpVerbal = dr.process(column="group", condition="Verbal")
    minRate = min(dpControl.liberalTargetAbsentSuspectId, dpVerbal.liberalTargetAbsentSuspectId)

    assert minRate == pytest.approx(0.09027777777777778, rel=1e-5)

def test_adv_stats_test2_csv_compare_two_pauc():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test2.csv")
    dr.cutData(column="previouslyViewedVideo", value=1, option="keep")
    dpControl = dr.process(column="group", condition="Control")
    dpVerbal = dr.process(column="group", condition="Verbal")
    minRate = min(dpControl.liberalTargetAbsentSuspectId, dpVerbal.liberalTargetAbsentSuspectId)
    dpControl = dr.process("group", "Control", pAUCLiberal=minRate)
    dpControl.calculateConfidenceBootstrap(nBootstraps=200)
    dpVerbal = dr.process("group", "Verbal", pAUCLiberal=minRate)
    dpVerbal.calculateConfidenceBootstrap(nBootstraps=200)
    [z,p] = dpControl.comparePAUC(dpVerbal)

    assert z == pytest.approx(1.2204034045897576, rel=1e-5)
    assert p == pytest.approx(0.22231198736511404, rel=1e-5)

def test_adv_stats_test1_csv_generate_sdt_data():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp, debug=True)
    mf.setEqualVariance()
    mf.fit()
    dr1 = mf.generateRawData(nGenParticipants=10000)

    # Need to process the synthetic data
    dp1 = dr1.process()

    # calculate uncertainties using bootstrap
    dp.calculateConfidenceBootstrap()
    dp1.calculateConfidenceBootstrap()

def test_adv_stats_test1_csv_power_analysis():
    import pyWitness
    import numpy
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp, debug=False)
    mf.setEqualVariance()
    mf.fit()

    for nGen in numpy.linspace(500, 5000, 9 + 1):
        drSimulated = mf.generateRawData(nGenParticipants=nGen)
        dpSimulated = drSimulated.process()
        dpSimulated.calculateConfidenceBootstrap(nBootstraps=2000)
        print(nGen, dpSimulated.liberalTargetAbsentSuspectId, dpSimulated.pAUC, dpSimulated.pAUC_low,
              dpSimulated.pAUC_high)