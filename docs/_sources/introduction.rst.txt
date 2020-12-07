============
Introduction
============

.. note:: 
   All plots and diagrams are made using pyWitness. The scripts used to make the plots are located in 
   ``pyWitness/manual/source/figures/``

Eye witness memory research
---------------------------

Reciever operator characteristic (ROC)
--------------------------------------

There are pacakges in R and Matlab to calculating pAUCs, smoothing ROCS, statistically comparing ROCs,etc. 

   * pROC: an open-source package for R and S+ to analyze and compare ROC curves
   * The ROC Toolbox: A toolbox for analyzing receiver-operating characteristics derived from confidence ratings

Signal Detection Theory 
-----------------------

Background to the pyWitness and the code
----------------------------------------

To keep a consistent set of analysis tools for eyewitness data it is important to keep a flexible 
internal data format.

Internal data format 
^^^^^^^^^^^^^^^^^^^^

.. list-table:: Data columns and allowed values
   :widths: 35 35 35 35
   :header-rows: 1

   * - lineupSize
     - targetLineup
     - responseType
     - confidence
   * - integer 
     - "targetPresent" 
     - "suspectId"
     - integer/float
   * -
     - "targetAbsent"
     - "fillerId"
     - 
   * - 
     - 
     - "rejectId"
     - 

Minimal example data file for an experiment 

.. list-table:: Example data file
   :widths: 35 35 35 35 35
   :header-rows: 1

   * - participantNumber 
     - lineupSize
     - targetLineup
     - responseType
     - confidence
   * - 1
     - 6
     - targetPesent
     - suspectId
     - 6
   * - 2
     - 6
     - targetAbsent
     - rejectId
     - 9
   * - 3 
     - 6
     - targetPresent
     - rejectId 
     - 1

.. note::
   Of course other columns can present in the data file, for examples labels for other experimental conditions 
   or data, demographic data or personal differenes.

Transforming data structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming data into pyWitness format can be time consuming and error prone.

.. list-table:: Example data file transformation (sdtlu)
   :widths: 35 35 
   :header-rows: 1

   * - pyWitness  
     - sdtlu
   * - lineupSize
     - lineup_size
   * - targetLineup
     - culprit_present
   * - targetPresent
     - present
   * - targetAbsent
     - absent
   * - responseType
     - id_type
   * - suspectId
     - suspect
   * - fillerId
     - filler
   * - rejectId
     - reject
   * - confidence
     - conf_level

.. note::
   Confidence can catagoral and so needs to be mapped to a number, so for example confidence could be low (1), 
   medium (2) or high (2).

