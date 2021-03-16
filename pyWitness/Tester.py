import openpyxl

class Tester :

    def __init__(self, excelFileName = ""):
        self.excelFileName = excelFileName
        self.excelFile     = openpyxl.load_workbook(self.excelFileName)

    def runTest(self, sheet = "Sheet1", column = 2):
        workSheet  = self.excelFile[sheet]
        data       = workSheet.cell(1,column).value
        model      = workSheet.cell(2,column).value
        paramSet   = workSheet.cell(3,column).value
        exclusions = workSheet.cell(4,column).value
        condition  = workSheet.cell(5,column).value
        binning    = workSheet.cell(6,column).value
        paramEstim = workSheet.cell(7,column).value
        maxiter    = workSheet.cell(8,column).value

        exec("dr = __import__('pyWitness')."+data,globals())
        exec("exclusionDict = "+exclusions,globals())

        if binning != "[]" :
            exec("binningArray ="+binning,globals())
            dr.collapseContinuousData(column = "confidence",bins = binningArray,labels=None)

        for k in exclusionDict :
            dr.cutData(k,exclusionDict[k])

        if condition != "" :
            conditionColumn = condition.split()[0]
            conditionValue  = condition.split()[1]
            globals()['dp'] = dr.process(conditionColumn,conditionValue)
        else :
            globals()['dp'] = dr.process()

        exec("mf = __import__('pyWitness').ModelFit"+model+"(dp,debug=True)",globals())
        exec("mf.set"+paramSet+"()",globals())

        if paramEstim == "True" :
            mf.setParameterEstimates()

        mf.fit(maxiter=int(maxiter))

        # get results
        mf.printParameters()

        return mf

    def fillResults(self, sheet = "Sheet1", column = 1):
        pass

    def compareResults(self, sheet = "Sheet1", column =1):
        pass



