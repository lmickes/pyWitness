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