import pytest

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

def test_03_plotting_test3_csv_plot_roc():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.plotROC()

def test_03_plotting_test3_csv_plot_cac():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.plotCAC()

def test_03_plotting_bar_chart():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.plotBarChart_Idrates()

def test_03_plotting_bar_chart_statistics_single():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.plotBarChart(bar1data="dPrime")

def test_03_plotting_bar_chart_statistics_couple():
    import pyWitness
    dr = pyWitness.DataRaw("../data/tutorial/test3.csv")
    dp = dr.process()
    dp.plotBarChart(bar1data="correctId", bar2data="falseId", chart1title="Correct Id", chart2title="False Id")