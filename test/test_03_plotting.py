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



