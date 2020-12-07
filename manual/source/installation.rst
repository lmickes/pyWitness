============
Installation
============


Requirements
------------

pyWitness is developed exclusively for Python 3, the numpy/scipy/matplotlib ecosystem are used for data analysis. 
These packages are required

  * python > 3.7
  * ipython
  * matplotlib 
  * numpy
  * scipy 
  * pandas

.. note :: 
   You will have to use a terminal of some kind for input of commands. On MacOS the program is called ``terminal`` and on Windows it
   is called ``PowerShell``.

.. warning :: 
   This tutorial assumes python is interactive python 3, with numpy and matplotlib, so the command ``ipython3 --pylab`` if you are 
   familiar with python and have an installation replace ``ipython3 --pylab`` with your own command to start python

Installation (PYTHON) 
---------------------

First you will need a suitable python environment. If you already have anaconda or miniconda installed, you can skip this part

  * Install `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ 
  * Open a terminal (MacOS) or PowerShell (Windows)
  * Install (ipython, numpy, scipy, pandas, matplotlib) by typing the following into your terminal/PowerShell
     * ``conda install ipython``
     * ``conda install numpy``
     * ``conda install scipy``
     * ``conda install pandas``
     * ``conda install matplotlib``
  * Start up python to test 
     * ``ipython3 --pylab``
     * Python should start up and input ``import numpy``
        * Provided there are no errors ``numpy`` has been installed, you can try this with the other packages installed with ``conda``
     

Installation (pyWitness)
------------------------

There are two ways to install pyWitness: Download the ZIP file or clone the GIT repository. If you are not comfortable 
with GIT (or don't have it installed on your computer), download the ZIP file. 

Download ZIP file
^^^^^^^^^^^^^^^^^

  * Download `pyWitness <https://github.com/lmickes/pyWitness>`_ (click on green code button -> Download ZIP)
  * Unpack ZIP file to a location of your choosing  
  * In a terminal/shell change directory to the pyWitness directory
  * ``pip3 install --editable . --user``

Clone GIT repository
^^^^^^^^^^^^^^^^^^^^

Open a terminal (linux in bash) and move to a suitable work directory

.. code-block :: shell
   
   git clone https://github.com/lmickes/pyWitness.git
   cd pyWitness   
   pip3 install --editable . --user

Testing it works
^^^^^^^^^^^^^^^^

Open a new terminal. Start your python interpreter (``ipython3 --pylab`` on the terminal/PowerShell) and import pyWitness

.. code-block :: python

   import pyWitness
   
If you get "pyWitness v0.1", it's installed and you can proceed to the tutorials.
      

