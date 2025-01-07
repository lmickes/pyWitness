improt pytest

def test_03_plotting_test1_csv_plot_roc():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dp = dr.process()
    dp.plotROC()

def test_03_plotting_test1_csv_plot_cac():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
    dp = dr.process()
    dp.plotCAC()

def test_03_plotting_test1_csv_plot_rac():
    import pyWitness
    drRAC = pyWitness.DataRaw("../data/tutorial/test1.csv")
    drRAC.collapseContinuousData(column="responseTime",
                                 bins=[0, 5000, 10000, 15000, 20000, 99999],
                                 labels=[1, 2, 3, 4, 5])
    dpRAC = drRAC.process(reverseConfidence=True, dependentVariable="responseTime")
    dpRAC.plotCAC()