def test_01_loading_test1_csv():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")

def test_01_loading_test1_csv_check_data():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.checkData()

def test_01_loading_test1_csv_column_values():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.columnValues("responseTime")

def test_01_loading_test1_xlxs():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.xlsx", "test1")