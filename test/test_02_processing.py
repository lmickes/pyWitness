import pytest

def test_02_processing_test1_csv():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dp = dr.process()

def test_02_processing_test1_csv_print_pivots_rates():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dp = dr.process()
    dp.printPivot()
    dp.printRates()

def test_02_processing_test1_csv_descriptive_stats():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dp = dr.process()
    dp.printDescriptiveStats()
    assert dp.dPrime == pytest.approx(1.9752208100241062, rel=1e-5)
    assert dp.pAUC == pytest.approx(0.020542013220820013, rel=1e-5)
    # overall correct ID rate
    assert dp.data_rates.loc[("targetPresent", "suspectId")].max() == pytest.approx(0.6196868008948546, rel=1e-5)
    # overall false ID rate
    assert dp.data_rates.loc[("targetAbsent", "suspectId")].max() == pytest.approx(0.0474040632054176, rel=1e-5)
    assert dp.data_rates.loc[("cac", "central")].max() == pytest.approx(0.976190, rel=1e-5)
    assert dp.data_rates.loc[("cac", "central")].min() == pytest.approx(0.461538, rel=1e-5)

def test_02_processing_test1_csv_response_time():
    import pyWitness
    drRAC = pyWitness.DataRaw("../data/tutorial/test1.csv")
    drRAC.collapseContinuousData(column="responseTime",
                                 bins=[0, 5000, 10000, 15000, 20000, 99999],
                                 labels=[1, 2, 3, 4, 5])
    dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")

def test_02_processing_test3_csv_descriptive_stats():
    # Showup case test
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.printDescriptiveStats()

def test_02_processing_test3_csv_data_rates():
    # Showup case test
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dr.collapseContinuousData("confidence", bins=[-11, -10, -7, 0, 7, 10, 11], labels=[-3, -2, -1, 1, 2, 3])
    dp = dr.process()
    s_cac = dp.data_rates.loc[("cac", "central")]
    s_carc = dp.data_rates.loc[("carc", "central")]
    cols = [-1, -2, -3]
    assert s_carc[cols].to_numpy() == pytest.approx(s_cac[cols].to_numpy(), rel=1e-5)
    assert dp.data_rates.loc[("cac", "central")].max() == pytest.approx(0.805970, rel=1e-5)
    assert dp.data_rates.loc[("cac", "central")].min() == pytest.approx(0.476562, rel=1e-5)
    assert dp.data_rates.loc[("carc", "central")].max() == pytest.approx(0.727273, rel=1e-5)
    assert dp.data_rates.loc[("targetPresent", "suspectId")].min() == pytest.approx(0.094737, rel=1e-5)
    assert dp.data_rates.loc[("targetAbsent", "rejectId")].max() == pytest.approx(0.691796, rel=1e-5)

def test_02_processing_test1ds_csv():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1ds.csv")
    dp = dr.process()