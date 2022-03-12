============
Installation
============


Requirements
------------

pyWitness is developed exclusively for Python 3, the numpy/scipy/matplotlib ecosystem are used for data analysis. The following packages are required

* python > 3.7
* ipython
* matplotlib 
* numpy
* scipy 
*  pandas

.. note :: 
   Use a terminal for inputting commands. On MacOS the program is called ``terminal`` and on Windows it
   is called ``PowerShell``.

.. warning :: 
   This tutorial assumes python is interactive python 3, with numpy and matplotlib, so the command ``ipython3 --pylab`` if you are familiar with python and have an installation replace ``ipython3 --pylab`` with your own command to start python.

Installing Python
-----------------

To install pyWitness, you need to install `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ 

Installing pyWitness
--------------------

Now you can install pyWitness in several ways.

1. using miniconda (the easiest installation; good for novice users)
2. using pip (if you already have python but not miniconda)
3. download the ZIP file (good for advanced users who want to see the code)
4. clone the git repository (good for people who want to contribute)


Miniconda install
^^^^^^^^^^^^^^^^^
Open a terminal (MacOS) or PowerShell (Windows) and install pyWitness by typing the following code line (or copy and paste) into your terminal or shell 

     * ``conda create --name pyWitness``
     * ``conda activate pyWitness``
     * ``conda install -c conda-forge -c lmickes pyWitness``
     

.. note :: 
   When you restart a terminal, you'll need to activate your pyWitness environment with ``conda activate pyWitness``


Pip install
^^^^^^^^^^^

    * `Download pyWitness-1.0-py3-none-any.whl <https://github.com/lmickes/pyWitness/releases/download/v1.0/pyWitness-1.0-py3-none-any.whl>`_
    * ``pip3 install pyWitness-1.0-py3-none-any.whl``

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
2. Start up python ``ipython3 --pylab`` on the terminal or shell
3. Import pyWitness by typing this code line (or copy and paste) into your terminal or shell

.. code-block :: python

   import pyWitness
   
If you get "pyWitness v0.1" it's installed and you can proceed to the tutorials.

