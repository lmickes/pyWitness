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

def test_02_processing_test1_csv_response_time():
    import pyWitness
    drRAC = pyWitness.DataRaw("../data/tutorial/test1.csv")
    drRAC.collapseContinuousData(column="responseTime",
                                 bins=[0, 5000, 10000, 15000, 20000, 99999],
                                 labels=[1, 2, 3, 4, 5])
    dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")

def test_02_processing_test3_csv_descriptive_stats():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.printDescriptiveStats()
