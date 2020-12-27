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
   You will have to use a terminal for inputting commands. On MacOS the program is called ``terminal`` and on Windows it
   is called ``PowerShell``.

.. warning :: 
   This tutorial assumes python is interactive python 3, with numpy and matplotlib, so the command ``ipython3 --pylab`` if you are 
   familiar with python and have an installation replace ``ipython3 --pylab`` with your own command to start python

Installing the PYTHON environment  
---------------------------------

You will need a suitable python environment. 

1. Install `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ 
2. Open a terminal (MacOS) or PowerShell (Windows) and install ipython, numpy, scipy, pandas, and matplotlib by typing each code line (or copy and paste) into your terminal or shell 
     * ``conda install ipython``
     * ``conda install numpy``
     * ``conda install scipy``
     * ``conda install pandas``
     * ``conda install matplotlib``
     * ``conda install openpyxl``
     * ``conda install xlrd``

3. Start up python to test 
     * ``ipython3 --pylab``
     * Python should start up and input ``import numpy``
        * Provided there are no errors ``numpy`` has been installed, you can try this with the other packages installed with ``conda``
     

Installing pyWitness
--------------------

There are two ways to install pyWitness: Download the ZIP file or clone the GIT repository. If you are not comfortable 
with GIT or do not have it installed on your computer, download the ZIP file. 

Download ZIP file
^^^^^^^^^^^^^^^^^

1. Download `pyWitness <https://github.com/lmickes/pyWitness>`_ (click on green code button -> Download ZIP)
2. Unpack ZIP file to a directory of your choosing  
3. In a terminal or shell change directory to the pyWitness directory

   * ``pip3 install --editable . --user``

Clone GIT repository
^^^^^^^^^^^^^^^^^^^^

Open a terminal (linux in bash) and move to a suitable work directory

.. code-block :: shell
   
   git clone https://github.com/lmickes/pyWitness.git
   cd pyWitness   
   pip3 install --editable . --user

To update pyWitness you will have to pull

.. code-block :: shell
   
   cd pyWitness
   git pull

Testing it works
^^^^^^^^^^^^^^^^

1. Open a new terminal 
2. Start your python interpreter (``ipython3 --pylab`` on the terminal or shell)
3. Import pyWitness by typing this code line (or copy and paste) into your terminal or shell

.. code-block :: python

   import pyWitness
   
If you get "pyWitness v0.1" it's installed and you can proceed to the tutorials.
      

