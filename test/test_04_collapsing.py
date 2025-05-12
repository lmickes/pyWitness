import pytest

def test_04_collapsing_test1_csv_categorical_data():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseCategoricalData(column='confidence',
                               map={0: 30, 10: 30, 20: 30, 30: 30, 40: 30, 50: 30, 60: 30,
                                    70: 75, 80: 75,
                                    90: 95, 100: 95})
    dp = dr.process()
    dp.plotCAC()

    assert dp.numberLineups == 890

def test_04_collapsing_test1_csv_continuous_data():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    dp.plotROC()

def test_04_collapsing_test1_csv_continuous_data_pauc():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dr.collapseContinuousData(column="confidence", bins=[-1, 60, 80, 100], labels=[1, 2, 3])
    dp = dr.process()
    print(dp.pAUC)

def test_04_collapsing_test3_csv_continuous_data() :
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dr.collapseContinuousData(column="confidence", bins=[-12, -9.5, -7.5, -5.5, 0, 5.5, 7.5, 9.5, 12.5],
                              labels=[1, 2, 3, 4, 5, 6, 7, 8])