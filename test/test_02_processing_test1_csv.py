def test_02_processing_test1_csv():
    import pyWitness
    dr = pyWitness.DataRaw("test1.csv")
    dp = dr.process()