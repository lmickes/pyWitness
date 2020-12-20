import pandas as _pandas

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
        self.dataMapping = dataMapping

        if self.fileName.find("csv") != -1 : 
            self.data     = _pandas.read_csv(fileName)
        elif self.fileName.find("xlsx") != -1 : 
            self.data     = _pandas.read_excel(fileName,excelSheet)
        
        self.dataAggFunc = ["confidence"]

        self.renameRawData()
                 
    def makeConfidenceBins(self,column = "confidence", nBins = 5) :
        minConf = self.data[column].min()
        maxConf = self.data[column].max()
        
        print('Data.makeConfidenceBins>',minConf,maxConf,nBins)

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

    def process(self, reverseConfidence = False) :
        self._data_processed = _DataProcessed(_pandas.pivot_table(self.data, columns='confidence', 
                                                                  index=['targetLineup','responseType'], 
                                                                  aggfunc={'confidence':'count'}),
                                              reverseConfidence = reverseConfidence,
                                              lineupSize        = self.data['lineupSize'][0])            
        return self._data_processed
