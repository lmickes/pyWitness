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

def test_02_processing_test1_csv_response_time():
    import pyWitness
    drRAC = pyWitness.DataRaw("../data/tutorial/test1.csv")
    drRAC.collapseContinuousData(column="responseTime",
                                 bins=[0, 5000, 10000, 15000, 20000, 99999],
                                 labels=[1, 2, 3, 4, 5])
    dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
