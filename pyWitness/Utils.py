import matplotlib.pyplot as _plt

def getColorOfLabeledFromGca(label) :
    axes     = _plt.gca()
    children = axes.get_children()

    for child in children :
        # print(child.get_label())

        if label == child.get_label() :
            fc = child.get_facecolor()[0]
            return fc

            #print(fc)