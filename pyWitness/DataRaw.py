import pandas as _pandas
import numpy as _np
import copy as _copy

from .DataProcessed import DataProcessed as _DataProcessed

dataMapSdtlu =  {"lineupSize":"lineup_size",
                 "targetLineup":"culprit_present",
                 "targetPresent":"present",
                 "targetAbsent":"absent",
                 "responseType":"id_type",
                 "suspectId":"suspect",
                 "fillerId":"filler",
                 "rejectId":"reject",
                 "confidence":"conf_level"}

dataMapPyWitness = None

class DataRaw :
    def __init__(self,
                 fileName, 
                 excelSheet = "data used",
                 dataMapping = dataMapPyWitness) :
        self.fileName = fileName
        self.excelSheet = excelSheet
        self.dataMapping = dataMapping

        self.dataAggFunc = ["confidence"]
        
        if fileName != '' : 
            self.loadData()
            self.renameRawData()

    def loadData(self) : 
        if self.fileName.find("csv") != -1 : 
            self.data     = _pandas.read_csv(self.fileName)
        elif self.fileName.find("xlsx") != -1 : 
            self.data     = _pandas.read_excel(self.fileName,self.excelSheet, engine='openpyxl')

    def makeConfidenceBins(self,column = "confidence", nBins = 5) :
        minConf = self.data[column].min()
        maxConf = self.data[column].max()
        
        print('Data.makeConfidenceBins>',minConf,maxConf,nBins)

    def rebinConfidence(self, bins = [41, 61, 81, 101]) :
        pass

    def setLineupSize(self,header) :
        self.dataMapping["lineupSize"] = header
    
    def setTargetLineup(self,header) : 
        self.dataMapping["targetLineup"] = header
        
    def setTargetLineupPresent(self, value) :
        self.dataMapping["targetPresent"] = value

    def setTargetLineupAbsent(self, value) :
        self.dataMapping["targetAbsent"] = value

    def setResponseType(self, header) :
        self.dataMapping["responseType"] = header

    def setResponseTypeSuspectId(self, value) :
        self.dataMapping["responseTypeSuspectId"] = value

    def setResponseTypeFillerId(self, value) :
        self.dataMapping["responseTypeFillerId"] = value

    def setResponseTypeReject(self, value) :
        self.dataMapping["responseTypeReject"] = value

    def descriptiveStatisticcs(self, column) :
        pass

    def renameRawData(self) :

        if self.dataMapping == None:
            return

        # column names 
        self.data.rename(columns={self.dataMapping['lineupSize']:'lineupSize',
                                  self.dataMapping['targetLineup']:'targetLineup',
                                  self.dataMapping['responseType']:'responseType',
                                  self.dataMapping['confidence']:'confidence'},
                         inplace=True)
        # column values
        self.data['targetLineup'] = self.data['targetLineup'].map({self.dataMapping['targetPresent']:'targetPresent',
                                                                   self.dataMapping['targetAbsent']:'targetAbsent'})

 
        self.data['responseType'] = self.data['responseType'].map({self.dataMapping['suspectId']:'suspectId',
                                                                   self.dataMapping['fillerId']:'fillerId',
                                                                   self.dataMapping['rejectId']:'rejectId'}) 

        # 0-60, 70-80, 90-100

    def collapseCategoricalData(self, column = "confidence", map = {0:30, 10:30, 20:30, 30:30, 40:30, 50:30, 60:30, 70:75, 80:75, 90:95, 100:95}, reload=False) : 
        # if the data need reloading?
        if reload : 
            self.loadData()

        # map column
        self.data[column] = self.data[column].map(map)

    def resampleWithReplacement(self) :
        data_copy = _copy.deepcopy(self)
        #data_copy = DataRaw('',self.excelSheet, self.dataMapping)        
        data_copy.data = _pandas.DataFrame(columns = self.data.columns) 

        nRows = self.data.shape[0]

        rowList = []
        for i in range(0,nRows,1) : 
            iRowRand = int(_np.random.rand()*nRows)
            rowList.append(self.data.iloc[iRowRand])
        
        data_copy.data = data_copy.data.append(rowList)

        return data_copy
        
    def process(self, column = '', condition = '', reverseConfidence = False) :
        if column != '' :
            self.dataSelected = self.data[self.data[column] == condition]
        else :
            self.dataSelected = self.data            
        
        self._data_processed = _DataProcessed(_pandas.pivot_table(self.dataSelected, columns='confidence', 
                                                                  index=['targetLineup','responseType'], 
                                                                  aggfunc={'confidence':'count'}),
                                              reverseConfidence = reverseConfidence,
                                              lineupSize        = self.data.iloc[0]['lineupSize'])            
        return self._data_processed
