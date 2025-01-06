def test_adv_stats_test1_csv_bootstrap():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=None)
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

def test_adv_stats_test2_csv_compare_two_pauc():
    import pyWitness
    dr = pyWitness.DataRaw("test2.csv")
    dr.cutData(column="previouslyViewedVideo", value=1, option="keep")
    dpControl = dr.process(column="group", condition="Control")
    dpVerbal = dr.process(column="group", condition="Verbal")
    minRate = min(dpControl.liberalTargetAbsentSuspectId, dpVerbal.liberalTargetAbsentSuspectId)
    dpControl = dr.process("group", "Control", pAUCLiberal=minRate)
    dpControl.calculateConfidenceBootstrap(nBootstraps=200)
    dpVerbal = dr.process("group", "Verbal", pAUCLiberal=minRate)
    dpVerbal.calculateConfidenceBootstrap(nBootstraps=200)
    dpControl.comparePAUC(dpVerbal)

