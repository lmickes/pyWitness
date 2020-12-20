============
Introduction
============

.. note:: 
   All plots and diagrams are made using pyWitness. The scripts used to make the plots are located in 
   ``pyWitness/manual/source/figures/``

Eyewitness identification research
----------------------------------

Eyewitnesses to crimes may try to identify the perpetrator from an identification procedure. One commonly used procedure is a lineup (identity parade in the UK). A lineup comprises the police suspect and fillers. A lineup with an innocent suspect is a target-absent lineup and a lineupw with a guilty suspect is a target-present lineup. Eyewitness can make filler IDs from either lineup, identify the innocent suspect (from a target-absent lineup) or guilty suspect (from a target-present lineup).

Receiver operating characteristic (ROC) analysis measures discriminability (the ability to distinguish innocent from guilty suspects), confidence accuracy characteristic (CAC) and response-time accuracy characteristic (RAC) analysis measure positive predictive value (the likelihood the identified suspect is guilty). pyWitness allows researchers to run these analyses. 

Theories about eyewitness identification have thus far been signal detection-based. pyWitness allows researchers to compare signal detection-based model fits. 

Receiver operator characteristic (ROC)
--------------------------------------

There are pacakges in R and MATLAB that calculate pAUCs, smooth ROCS, and statistically comparing pAUCs. 

   * pROC: an open-source package for R and S+ to analyze and compare ROC curves
   * The ROC Toolbox: A MATLAB toolbox for analyzing ROCs derived from confidence ratings

Signal Detection Theory 
-----------------------

   * sdtlu: an open-source package for R to run signal detection model fits on lineup data

Goals of pyWitness
------------------

   * Bin and pivot raw data to rates (process raw data)
   * Plot and compare ROC, CAC and RAC curves
   * Calculate pAUC and compute statistial tests
   * Perform statistical tests on CAC/RAC curves
   * Fit signal detection models to the processed data
   * Monte Carlo simulation of raw data
   * Teaching aid to create signal detection model plots

Background to the pyWitness and the code
----------------------------------------

Our goal with pyWitness is to create a consistent set of analysis tools for any eyewitness memory researcher to use for lineup data. Importantly, there is a flexible internal data format.

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
   Confidence can verbal and so needs to be mapped to a number. For example, confidence could be low (1), 
   medium (2) or high (3).

