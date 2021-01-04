Advanced tutorials
==================

Loading raw data excel format
-----------------------------

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

Processing data for a single condition
--------------------------------------

So a single data file might have multiple different experimental condtions. So imagine your data file 
has a column labelled ``Condition`` and the values for each participant is either ``Sequential`` or 
``Simultaneous``. So to proccess only the ``Sequential`` participants the following options are required
for DataRaw.process() 

.. code-block :: python
   :linenos:
   :emphasize-lines: 3

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dp = dr.process("Condition","Sequential")   

So if you had a file with multiple conditions it would be very straight forward to make multiple 
``DataProcessed`` for each condition, so like the following 

.. code-block :: python
   :linenos:
   :emphasize-lines: 3-4

   import pyWitness
   dr = pyWitness.DataRaw("test1.csv")
   dpSeq = dr.process("Condition","Sequential")   
   dpSim = dr.process("Condition","Simultaneous")   

Loading processed data 
----------------------

You might already have processed the raw data. It is possible to load a file to perform model fits etc. The processed data needs 
to be in the following CSV format. This is basically the same format as the pivot table stored in ``DataProcessed``. 

.. list-table:: Processed data columns and allowed values
   :widths: 35 15 15 15 15 15 15 15 15 15 15 15 
   :header-rows: 0

   * - confidence 
     - 0 
     - 10
     - 20
     - 30
     - 40
     - 50 
     - 60
     - 70
     - 80 
     - 90
     - 100
   * - targetAbsent fillerId 
     - 3
     - 7
     - 7
     - 11
     - 16
     - 26
     - 30
     - 31
     - 19
     - 13
     - 10
   * - targetAbsent rejectId
     - 4
     - 5
     - 5
     - 6
     - 11
     - 28
     - 39
     - 57
     - 75
     - 46
     - 66
   * - targetPresent fillerId
     - 2
     - 1
     - 3
     - 4
     - 10
     - 9
     - 9
     - 17
     - 16
     - 6
     - 4
   * - targetPresent rejectId 
     - 4
     - 3
     - 
     - 9
     - 10
     - 23
     - 11
     - 19
     - 25
     - 18
     - 25
   * - targetPresent suspectId
     - 3
     - 1
     - 4 
     - 5
     - 11 
     - 19
     - 44
     - 77
     - 55
     - 37
     - 47

.. note :: 
   If the ``targetAbsent suspectId`` row is not present it is estimated by ``(targetAbsent fillerId)/lineupSize``

This data is stored in ``data/tutorials/test1_processed.csv``

.. code-block :: python
   :linenos:
   :emphasize-lines: 2

   import pyWitness
   dp = pyWitness.DataProcessed("test1_processed.csv", lineupSize = 6)
   
Using instances of raw data, processed data and model fits
----------------------------------------------------------

Using an object orientated approach allows multiple instances (objects) to be created and manipulated. This allows lots of different 
data file, variations on the processed data and model fits to be manipulated simultanuously in a single Python session.

A good example is collapsing data, one might want to check the effect of rebinning the data. So in the following example the ``test1.csv`` is processed twice, once with the original binning (``dr1`` and ``dp1``) and one with 3 confidence bins (``dr2`` and ``dp2``)

.. code-block :: python

   import pyWitness
   dr1 = pyWitness.DataRaw("test1.csv")
   dr2 = pyWitness.DataRaw("test1.csv")
   
   dr2.collapseCatagoricalData(column='confidence',
                               map={0: 30, 10: 30, 20: 30, 30: 30, 40: 30, 50: 30, 60: 30, 
                                    70: 75, 80: 75, 
                                    90: 95, 100: 95})
   dp1 = dr1.process()
   dp2 = dr2.process()

   dp1.plotCAC()   
   dp2.plotCAC()

Overlaying plots
----------------

In general each ``plotXXX`` function does not create a canvas, so to overlay plots the functions need to be called sequentially in order.

To make a legend the plots need to be given a label. So this example is the same as the 

.. code-block :: python
   :linenos:
   :emphasize-lines: 12-16

   import pyWitness
   dr1 = pyWitness.DataRaw("test1.csv")
   dr2 = pyWitness.DataRaw("test1.csv")
   
   dr2.collapseCatagoricalData(column='confidence',
                               map={0: 30, 10: 30, 20: 30, 30: 30, 40: 30, 50: 30, 60: 30, 
                                    70: 75, 80: 75, 
                                    90: 95, 100: 95})
   dp1 = dr1.process()
   dp2 = dr2.process()

   dp1.plotCAC(label = "11 bins")   
   dp2.plotCAC(label = "3 bins")
   
   import matplotlib.pyplot as _plt
   _plt.legend()

.. figure:: images/test1_overlay.jpg
   :alt: CAC for test1.csv with two different binning

Generating data from signal detection model
-------------------------------------------


