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