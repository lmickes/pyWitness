def test_05_fitting_test1_csv_indep_obs_eqvar():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.setEqualVariance()
    mf.fit()

def test_05_fitting_test1_csv_indep_obs_uneqvar_print_parameters():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    mf = pyWitness.ModelFitIndependentObservation(dp)
    mf.printParameters()

def test_05_fitting_test1_csv_best_rest():
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf_br = pyWitness.ModelFitBestRest(dp)

def test_05_fitting_test1_csv_ensemble():
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf_en = pyWitness.ModelFitEnsemble(dp)

def test_05_fitting_test1_csv_integration():
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence")
    dp = dr.process()
    mf_in = pyWitness.ModelFitIntegration(dp)

