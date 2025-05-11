import pytest

def test_01_loading_test1_csv():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dp = dr.process()
    assert dp.numberLineups == 890
    assert dp.numberTALineups == 443
    assert dp.numberTPLineups == 447

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

def test_01_loading_test3_csv() :
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")

def test_01_loading_test1ds_csv() :
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1ds.csv")