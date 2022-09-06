======================
Using pyWitness from R
======================


.. warning :: 
   You still need to follow the python installation instructions as the package is fundamentally python which is just called from R
 
pyWitness is developed exclusively in Python 3, so to use it in R we need to install a library to interface with python (reticulate). First install reticulate in R

     * ``install.packages("reticulate")``

Then it should be possible to import the python

     * ``pyw <- import("pyWitness")``

If this causes an import error, you might need to point to your conda version of pytohn

     * ``use_python("USRHOME/opt/miniconda3/bin/python")``


.. warning :: 
   If you want to use pyWitness in jupyter labbook there are some issues with python output which might go to the terminal and not to the notebook. Similar for the plots, which will open but not inline in the notebook