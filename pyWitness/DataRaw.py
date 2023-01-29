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
    '''
    
    DataRaw : wrapper for raw eyewitness data

    :param fileName: input file name (either csv or excel)
    :type fileName: str
    :param excelSheet: name of the excel sheet to use 
    :type excelSheet: str
    :param dataMapping: python map to change columns and values
    :type dataMapping: map

    '''

    def __init__(self,
                 fileName, 
                 excelSheet = "data used",
                 dataMapping = dataMapPyWitness) : 

        self.data         = None 
        '''Data frame of all raw data for processing'''
        
        self.dataSelected = None 
        '''Data frame of selected data for processing'''

        self.fileName = fileName
        '''Raw data file name'''

        self.excelSheet = excelSheet
        '''Excel sheet name'''

        self.dataMapping = dataMapping
        '''Map of columns and values for renaming'''

        self.dataAggFunc = ["confidence"]
        
        if fileName != '' :
            self.loadData()
            self.renameRawData()
            self.checkData()
        else :
            self.data = None

        self.collapseContinuous = False

    def loadData(self) :
        '''
        Load data from file using panda functions

        :rtype: None
        '''
 
        if self.fileName.find("csv") != -1 : 
            self.data     = _pandas.read_csv(self.fileName)
        elif self.fileName.find("xlsx") != -1 : 
            self.data     = _pandas.read_excel(self.fileName,self.excelSheet, engine='openpyxl')
        elif self.fileName.find("sav") != -1 :
            self.data = _pandas.read_spss(self.fileName)

    def setLineupSize(self,header) :
        '''
        Set the lineupSize column name in the dataMapping

        :rtype: None
        '''
        
        self.dataMapping["lineupSize"] = header
    
    def setTargetLineup(self,header) : 
        '''
        Set the targetLineup column name in the dataMapping

        :rtype: None
        '''

        self.dataMapping["targetLineup"] = header
        
    def setTargetLineupPresent(self, value) :
        '''
        Set the targetPresent value in the dataMapping

        :rtype: None
        '''

        self.dataMapping["targetPresent"] = value

    def setTargetLineupAbsent(self, value) :
        '''
        Set the targetAbsent value in the dataMapping

        :rtype: None
        '''

        self.dataMapping["targetAbsent"] = value

    def setResponseType(self, header) :
        '''
        Set the responseType column name in the dataMapping

        :rtype: None
        '''

        self.dataMapping["responseType"] = header

    def setResponseTypeSuspectId(self, value) :
        '''
        Set the suspectId value in the dataMapping

        :rtype: None
        '''

        self.dataMapping["responseTypeSuspectId"] = value

    def setResponseTypeFillerId(self, value) :
        '''
        Set the fillerId value in the dataMapping

        :rtype: None
        '''

        self.dataMapping["responseTypeFillerId"] = value

    def setResponseTypeRejectId(self, value) :
        '''
        Set the reject value in the dataMapping

        :rtype: None
        '''

        self.dataMapping["responseTypeRejectId"] = value

    def descriptiveStatistics(self, column) :
        pass

    def renameRawData(self) :
        ''' 
        Remap column and values to a consistent set

        :rtype: None
        '''

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

    def checkData(self):

        print('DataRaw.checkData>')

        lineupSize   = _np.unique(self.data['lineupSize'])
        targetLineup = _np.unique(self.data['targetLineup'])
        responseType = _np.unique(self.data['responseType'])
        confidence   = _np.unique(self.data['confidence'])

        print('DataRaw.checkData> columns       :',self.data.columns.values)
        print('DataRaw.checkData> lineupSize    :',lineupSize)
        print('DataRaw.checkData> targetLineup  :',targetLineup)
        print('DataRaw.checkData> responseType  :',responseType)
        print('DataRaw.checkData> confidence    :',confidence)
        print('DataRaw.checkData> number trials :',len(self.data))

    def columnValues(self,columnName):

        if not self.checkColumn(columnName) :
            return

        uniqueValues = _np.unique(self.data[columnName])
        print('DataRaw.columnValues>           :',columnName,uniqueValues)

    def checkColumn(self,columnName):
        try :
            self.data[columnName]
            return True
        except :
            print("DataRaw.checkColumn> Column not present :",columnName)
            return False


    def collapseTargetAbsentSuspectId(self):

        '''
        Convert targetAbsent suspectIds to targetAbsent fillerIds

        :return:
        '''
        c = _np.logical_and(self.data['targetLineup'] == "targetAbsent", self.data['responseType'] == "suspectId")
        self.data['responseType'][c] = "fillerId"

    def collapseCategoricalData(self, 
                                column = "confidence", 
                                map = {0:30, 10:30, 20:30, 30:30, 40:30, 50:30, 60:30, 
                                       70:75, 80:75, 
                                       90:95, 100:95}, 
                                reload=False) : 
        '''
        Take values of column and convert to new values in map
        
        :param column: data column to map
        :type column: str
        :param map: value map
        :type map: map
        :param reload: flag to reaload data
        :type reload: bool 
        :rtype: None        
        '''

        # dict (list in R) cannot have numbers as keys
        newMap = {}
        for k in map :
            newMap[int(k)] = map[k]

        map = newMap

        # if the data need reloading?
        if reload : 
            self.loadData()

        # map column
        self.data[column] = self.data[column].map(map)


    def collapseContinuousData(self, 
                               column = "confidence",
                               bins = [-1,60,80,100],
                               labels= [1,2,3]
                               ) :
        '''
        Take values of column and rebin to new keys in bins

        :param column: data column to create bin catagories  
        :type column: str
        :param bins: Map of categories and bins  
        :type bins: map

        :rtype:None 
        '''

        if self.collapseContinuous :
            raise Exception("Already binned confidence")

        # If there are no labels generate them
        if labels == None :
            labels = range(1,len(bins))

        self.collapseContinuous       = True
        self.collapseContinuousColumn = column
        self.collapseContinuousBins   = bins
        self.collapseContinuousLabels = labels

        column_original = column+"_original"

        self.data.rename(columns = {column:column_original}, inplace= True)

        dataToBin = self.data[column_original]

        dataBinned = _pandas.cut(dataToBin,bins,labels = labels)
        self.data.insert(self.data.columns.get_loc(column_original)+1, column, dataBinned)

    def resampleWithReplacement(self) :
        ''' 
        Resample data with replacement and return copy of object. Required for bootstrapping the confidence interval calcualations
        '''
 
        data_copy = DataRaw('',self.excelSheet, self.dataMapping)        
        data_copy.data = self.data.sample(n = self.data.shape[0],replace = True)

        if self.collapseContinuous :
            data_copy.collapseContinuous       = self.collapseContinuous
            data_copy.collapseContinuousColumn = self.collapseContinuousColumn
            data_copy.collapseContinuousBins   = self.collapseContinuousBins
            data_copy.collapseContinuousLabels = self.collapseContinuousLabels

        return data_copy

    def shuffle(self):
        self.data = self.data.sample(frac=1).reset_index(drop=True)

    def resampleParticipantTrial(self, nTrial = 100, iParticipant = 0):

        # TODO : Guard against going out of data range (iParticipant+1)*nTrial > length of data frame

        data_copy = DataRaw('', self.excelSheet, self.dataMapping)
        data_copy.data = self.data[iParticipant*nTrial:(iParticipant+1)*nTrial]

        if self.collapseContinuous :
            data_copy.collapseContinuous       = self.collapseContinuous
            data_copy.collapseContinuousColumn = self.collapseContinuousColumn
            data_copy.collapseContinuousBins   = self.collapseContinuousBins
            data_copy.collapseContinuousLabels = self.collapseContinuousLabels

        return data_copy


    def addParticipant(self, participantId = None, lineupSize = 6, targetLineup = "targetPresent",
                       responseType = "suspectId", confidence = 0, n = 1):

        if not isinstance(self.data,_pandas.DataFrame):
            self.iParticipant = 1
            self.data = _pandas.DataFrame(columns = ['participantId','lineupSize','targetLineup','responseType','confidence'], dtype=int)

        for i in range(0,int(n),1) :
            #self.data = self.data.append({"participantId":self.iParticipant,
            #                              "lineupSize":lineupSize,
            #                              "targetLineup":targetLineup,
            #                              "responseType":responseType,
            #                              "confidence":confidence},
            #                              ignore_index=True)
            self.data = _pandas.concat([self.data, _pandas.DataFrame({"participantId":[self.iParticipant],
                                                                      "lineupSize":[lineupSize],
                                                                      "targetLineup":[targetLineup],
                                                                      "responseType":[responseType],
                                                                      "confidence":[confidence]})])
            self.iParticipant += 1

    def cutData(self, column = '', value = '', option="keep"):
        '''

        Data to keep

        :param column:
        :param value:
        :return:
        '''

        if type(value) == str or type(value) == int or type(value) == float:
            value = [value]

        if option == "keep":
            first = True
            for v in value :
                c = self.data[column] == v
                if first :
                    cut = c
                    first = False
                else :
                    cut = _np.logical_or(cut,c)

            self.data = self.data.loc[cut]
            return (cut*1).sum()

        elif option == "cut":
            cut       = self.data[column] != value
            self.data = self.data.loc[cut]
            return (cut*1).sum()

    def isDesignateId(self) :
        if (self.data['responseType'] == "designateId").any():
            return True
        else :
            return False

    def removeDesignates(self):
        self.data['responseType'] = self.data['responseType'].map({'designateId':'fillerId',
                                                                   'suspectId':'suspectId',
                                                                   'fillerId':'fillerId',
                                                                   'rejectId':'rejectId'})

    def process(self, column = '', condition = '', reverseConfidence = False, pAUCLiberal = 1.0, levels = None, option = "all", dependentVariable = "confidence") :
        '''
        Process the raw data and returns DataProcessed object

        :param column: Dataframe column which is tselected for processing
        :type column: str
        :param condition: condition for the column
        :type condition: str
        :param reverseConfidence: flip the confidence (usually low number to high)
        :type condition: bool
        :rtype: DataProcessed
        '''


        self.processColumn = column
        self.processCondition = condition
        self.processReverseConfidence = reverseConfidence
        self.dependentVariable = dependentVariable

        if column != '' :
            self.dataSelected = self.data[self.data[column] == condition]
        else :
            self.dataSelected = self.data            

        self.pAUCLiberal = pAUCLiberal

        self._data_processed = _DataProcessed(dataRaw           = self,
                                              reverseConfidence = reverseConfidence,
                                              lineupSize        = self.dataSelected.iloc[0]['lineupSize'],
                                              pAUCLiberal       = pAUCLiberal,
                                              levels            = levels,
                                              option            = option)
        return self._data_processed

    def writeCsv(self, fileName):
        '''
        Write raw data Dataframe to csv file

        :param fileName: File name of the excel file to write
        :type fileName: str
        '''

        self.data.to_csv(fileName)


    def writeExcel(self, fileName, engine = 'openpyxl'):
        '''
        Write raw data Dataframe to excel file

        :param fileName: File name of the excel file to write
        :type fileName: str
        :param engine: Excel output engine
        :type engine: str
        :rtype: None

        '''

        self.data.to_excel(fileName, engine = engine)