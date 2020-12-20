Tutorials
=========

.. note::
   The data files used in this tutorial are stored in ``pyWitness/data/``. It is a good idea to copy these files to your working 
   directory

.. warning::
   error bars, collapse confidence

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
To process the raw data the function ``process`` needs to be called on a raw data object. 

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


Fitting signal detection models to data
---------------------------------------

Generating data from signal detection model
-------------------------------------------

