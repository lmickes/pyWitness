import pandas as _pandas

import matplotlib.pyplot as _plt

import numpy as _np

# "mediumvioletred"
# "teal"
# "hotpink"
# "steelblue"
# "limegreen"
# "mediumspringgreen"
# "tomato"
# "cornflowerblue"

def forestPlot(fileName):
	#load csv data into pandas data frame
	data = _pandas.read_csv(fileName)#,index_col=0)
	data.sort_values("n",inplace=True, ascending = False)

	#compute mean, variance, and relative frequency
	mean = (data["pAUC diff"]*data["n"]).sum()/data["n"].sum()
	var = (data["pooled sd"]**2*data["n"]).sum()/data["n"].sum()
	print(mean,var)

	mean = (data["pAUC diff"]/data["pooled sd"]**2).sum()/(1/data["pooled sd"]**2).sum()
	var = 1/(1/data["pooled sd"]**2).sum()
	relFreq = data["n"]/data["n"].sum()

	print(mean,var)

	#plotting
	_plt.errorbar(data["pAUC diff"],data["author"],None,data["pooled sd"], ".",color = "black",capsize = 3)
	_plt.scatter(data["pAUC diff"],data["author"],s = relFreq*500,marker = "o",color = "black")
	_plt.axvline(0,color = "cornflowerblue", linestyle = "dashed")
	_plt.axvline(mean,color = "black")
	_plt.axvline(mean - _np.sqrt(var),color = "black",linestyle = "dotted")
	_plt.axvline(mean + _np.sqrt(var),color = "black",linestyle = "dotted")
	_plt.xlim(-0.04,0.04)
	_plt.xlabel("pAUC difference")
	#_plt.legend(loc=2)
	_plt.tight_layout()
	
	_plt.savefig("ForestPlot.pdf")

	return data