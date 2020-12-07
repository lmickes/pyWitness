Tutorials
=========

.. note::
   The data files used in this tutorial are stored in ``pyWitness/data/tutorial``. It is a good idea to copy these files to your working 
   directory

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

Fitting signal detection models to data
---------------------------------------

Generating data from signal detection model
-------------------------------------------

