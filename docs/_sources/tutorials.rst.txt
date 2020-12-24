Tutorials
=========

.. note::
   The data files used in this tutorial are stored in ``pyWitness/data/``. It is a good idea to copy these files to your working 
   directory. This tutorial builds up! Between each example and previous examples the new lines of code are highlighted in yellow.

.. warning::
   error bars, Processing raw experimental data for a particular experimental condition, Calculating pAUC and performing statistical tests, 
   Fitting signal detection models to data

Loading raw experimental data
-----------------------------

A single Python class ``pyWitness.DataRaw`` is used to load raw data in either ``csv`` or ``excel`` format. The format of ``test.csv``
is the same as that described in the introduction. 

.. code-block :: python 

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")

If the file is in ``excel`` format you will need to specify which sheet the raw data is stored in 

.. code-block :: python 
      
   import pyWitness
   dr = pyWitness.DataRaw("test2.xlsx",excelSheet = "raw data")

Transforming data into common format
------------------------------------

The raw experimental data does not have to be in the internal format used by pyWitness. As the data is loaded is it possible to replace 
the name of the data columns and the values stored.

.. code-block :: python 

   import pyWitness
   dr = pyWitness.DataRaw("test2.csv", dataMapping = {"lineupSize":"lineup_size",
                                                     "targetLineup":"culprit_present",
						     "targetPresent":"present",
						     "targetAbsent":"absent",
						     "responseType":"id_type",
						     "suspectId":"suspect",
						     "fillerId":"filler",
						     "rejectId":"reject",
						     "confidence":"conf_level"}))


Processing raw experimental data
--------------------------------
To process the raw data the function ``process`` needs to be called on a raw data object. The calculates the cumulative rates from the raw data. 

.. code-block :: python 
   :linenos:
   :emphasize-lines: 3

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dp = dr.process()

Once ``process`` is called two ``DataFrames`` are created one which contains a pivot table and another that contains rates

.. code-block :: python 
   :linenos:
   :emphasize-lines: 4-5

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dp = dr.process()
   dp.printPivot()
   dp.printRates()

Here is the output of the ``dp.printPivot()``

.. code-block :: console

                              confidence                                                          
   confidence                        0    10   20    30    40    50    60    70    80    90    100
   targetLineup  responseType                                                                     
   targetAbsent  fillerId            3.0  7.0  7.0  11.0  16.0  26.0  30.0  31.0  19.0  13.0  10.0
                 rejectId            4.0  5.0  5.0   6.0  11.0  28.0  39.0  57.0  75.0  46.0  66.0
   targetPresent fillerId            2.0  1.0  3.0   4.0  10.0   9.0   9.0  17.0  16.0   6.0   4.0
                 rejectId            4.0  3.0  NaN   9.0  10.0  23.0  11.0  19.0  25.0  18.0  25.0
                 suspectId           3.0  1.0  4.0   5.0  11.0  19.0  44.0  77.0  55.0  37.0  47.0

And here is the output of the ``dp.printRates()``

.. code-block :: console

                              confidence                                                                                                    
   confidence                        100       90        80        70        60        50        40        30        20        10        0  
   targetLineup  responseType                                                                                                               
   cac                          0.965753  0.944681  0.945559  0.937120  0.897959  0.814286  0.804878  0.731707  0.774194  0.461538  0.857143 
   rf                           0.146660  0.118031  0.175289  0.247614  0.147664  0.070316  0.041185  0.020593  0.015570  0.006529  0.010547
   targetAbsent  fillerId       0.019417  0.044660  0.081553  0.141748  0.200000  0.250485  0.281553  0.302913  0.316505  0.330097  0.335922
                 rejectId       0.128155  0.217476  0.363107  0.473786  0.549515  0.603883  0.625243  0.636893  0.646602  0.656311  0.664078
                 suspectId      0.003236  0.007443  0.013592  0.023625  0.033333  0.041748  0.046926  0.050485  0.052751  0.055016  0.055987
   targetPresent fillerId       0.007533  0.018832  0.048964  0.080979  0.097928  0.114878  0.133710  0.141243  0.146893  0.148776  0.152542
                 rejectId       0.047081  0.080979  0.128060  0.163842  0.184557  0.227872  0.246704  0.263653       NaN  0.269303  0.276836
                 suspectId      0.088512  0.158192  0.261770  0.406780  0.489642  0.525424  0.546139  0.555556  0.563089  0.564972  0.570621

.. note::
   In the example there is no ``suspectId`` for ``targetAbsent`` lineups. Here the ``targetAbsent.suspectId`` is estimated as ``targetAbsent.fillerId/lineupSize`` 

Plotting ROC curves
-------------------

.. code-block :: python 
   :linenos:
   :emphasize-lines: 4

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dp = dr.process()
   dp.plotROC()

.. figure:: images/test1_roc.jpg
   :alt: ROC for test1.csv

.. note:: 
   The symbol size is the relative frequency and can be changed by setting ``dp.plotROC(relativeFrequencyScale = 400)``

Plotting CAC curves 
-------------------

.. code-block :: python 
   :linenos:
   :emphasize-lines: 4

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dp = dr.process()
   dp.plotCAC()

.. figure:: images/test1_cac.jpg
   :alt: CAC for test1.csv

Plotting RAC curves
-------------------

Collapsing the confidence binning
---------------------------------

The example in this tutorial as 11 confidence levels (0, 10, 20, 30, 40, 50, 60, 70, 80, 90 and 100). Typically catagorical confidence levels need to be binned or collapsed. This is best performed on the raw data before calling ``process()``. This is done with the ``collapseCatagoricalData`` method of ``DataRaw``. This is shown in example below, where the new bins are (0-60 map to 30, 70-80 to 75 and 90-100 to 95).

.. code-block :: python 
   :linenos:
   :emphasize-lines: 3-6
  
   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dr.collapseCatagoricalData(column='confidence',
                              map={0: 30, 10: 30, 20: 30, 30: 30, 40: 30, 50: 30, 60: 30, 
                                   70: 75, 80: 75, 
                                   90: 95, 100: 95})
   dp = dr.process()
   dp.plotCAC()   

.. figure:: images/test1_rebinned.jpg
   :alt: Rebinned CAC for test1.csv 

Calculating pAUC and performing statistical tests
-------------------------------------------------

Fitting signal detection models to data
---------------------------------------

Writing results to file 
-----------------------

The internal dataframes can be written to either ``csv`` or ``xlsx`` file format for further analysis. There are four functions belonging to ``DataProcessed``. 

   * ``writePivotExcel`` writes the pivot table to excel
   * ``writePivotCsv`` writes the pivot table to csv
   * ``writeRatesExcel`` writes the cummulative rates table to excel
   * ``writeRatesCsv`` writes the cummulative rates table to csv

The string argument for the functions is the file name. 

.. code-block :: python 
   :linenos:
   :emphasize-lines: 4-7
   
   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dp = dr.process()  
   dp.writePivotExcel("test1_pivot.xlsx")
   dp.writePivotCsv("test1_pivot.csv")
   dp.writeRatesExcel("test1_rates.xlsx")
   dp.writeRatesCsv("test1_rates.csv")

.. figure:: images/test1_pivot_excel.jpg

.. figure:: images/test1_rates_excel.jpg

Loading binned data 
-------------------


