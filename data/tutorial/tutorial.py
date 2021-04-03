# code to convert published data into files for tutorials

import pandas as _pandas
import numpy  as _np
import copy   as _copy

def makeTest1Csv(lineupSize = 6) :
    data     = _pandas.read_excel('../published/2019_Seale-CarlisleColloffFloweWellsWixtedMickes/Seale-Carlisle_et_al_raw_data.xlsx',
                                  'Study 1 Laboratory Data')

    participantId  = data['Participant Number']
    targetLineup1  = data['Target Absent or Target Present']
    response1      = data['Said Absent or Said Present']
    accuracy1      = data['Accuracy']
    confidence1    = data['Confidence']
    responseTime   = data['Response Time']
    
    targetLineup   = []
    response       = [] 
    lineupSizeList = []

    for pId in participantId : 
        i = pId-1 

        if targetLineup1[i] == "Target Absent" : 
            targetLineup.append("targetAbsent")
            if response1[i] == "Said Present" :
                response.append("fillerId")
            elif response1[i] == "Said Absent" :
                response.append("rejectId")
            else :
                response.append("none")
        elif targetLineup1[i] == "Target Present" :
            targetLineup.append("targetPresent") 
            if   response1[i] == "Said Present" and accuracy1[i] == 1: 
                response.append("suspectId") 
            elif response1[i] == "Said Present" and accuracy1[i] == 0: 
                response.append("fillerId")
            elif response1[i] == "Said Absent" :
                response.append("rejectId")
            else :
                response.append("none")
        else : 
            reponse.append("none")

        lineupSizeList.append(lineupSize)

        # print(i, targetLineup[i], response1[i], accuracy1[i],response1[i])

    dataNew = _pandas.DataFrame()
    dataNew['participantId'] = participantId
    dataNew['lineupSize']    = lineupSizeList
    dataNew['targetLineup']  = targetLineup
    dataNew['responseType']  = response
    dataNew['confidence']    = confidence1
    dataNew['responseTime']  = responseTime

    dataNew.to_csv("test1.csv")

    return dataNew

def makeTest2DataFrame() :
    data     = _pandas.read_excel('../published/2017_Wilson_SealeCarlisle_Mickes/Wilson_SealeCarlisle_Mickes2017.xlsx','Exp1_2')

    expNumber             = data['Exp']
    idNumber              = data['ID #']
    age                   = data['Age']
    gender                = data['Gender']
    group                 = data['Group']
    targetLineup          = data['Target Absent or Present']
    confidence            = data['Confidence']
    accuracy              = data['Accuracy']
    response1             = data['Present or Absent Response']
    previouslyViewedVideo = data['Previously Viewed Video']
    lineupSize            = _copy.copy(expNumber)
    responseType          = _copy.copy(expNumber)


    lineupSize[:]         = 6
    targetLineup.replace({"Target-absent":"targetAbsent","Target-present":"targetPresent"}, inplace=True)

    tafid                 = _np.logical_and(targetLineup == "targetAbsent",_np.logical_and(response1 == "Present", accuracy == 0))
    tarid                 = _np.logical_and(targetLineup == "targetAbsent",_np.logical_and(response1 == "Absent",  accuracy == 1))
    tpfid                 = _np.logical_and(targetLineup == "targetPresent",_np.logical_and(response1 == "Present", accuracy == 0))
    tpsid                 = _np.logical_and(targetLineup == "targetPresent",_np.logical_and(response1 == "Present", accuracy == 1))
    tprid                 = _np.logical_and(targetLineup == "targetPresent",_np.logical_and(response1 == "Absent", accuracy == 0))

    responseType[tafid] = "fillerId"
    responseType[tarid] = "rejectId"
    responseType[tpfid] = "fillerId"
    responseType[tpsid] = "suspectId"
    responseType[tprid] = "rejectId"

    cut = _np.logical_and(expNumber == 1, previouslyViewedVideo == 1)

    dataNew = _pandas.DataFrame()
    dataNew['participantId'] = idNumber[cut]
    dataNew['lineupSize']    = lineupSize[cut]
    dataNew['targetLineup']  = targetLineup[cut]
    dataNew['responseType']  = responseType[cut]
    dataNew['confidence']    = confidence[cut]
    dataNew['age']           = age[cut]
    dataNew['gender']        = gender[cut]
    dataNew['group']         = group[cut]


    return dataNew


def makeTest2Csv() :
    df = makeTest2DataFrame()
    df.to_csv("test2.csv")

def makeTest2Xlsx() :
    df = makeTest2DataFrame()
    df.to_excel("test2.xlsx")

def makeTest3Csv() :
    data     = _pandas.read_excel('../published/2017_Wilson_SealeCarlisle_Mickes/Wilson_SealeCarlisle_Mickes2017.xlsx','Exp3')

    participantId = _np.arange(data.shape[0])
    group                 = data['Group']
    confidence            = data['Confidence']
    targetLineup          = data['Target or Lure']
    responseType          = data['Target or Lure Response']
    accuracy              = data['Accuracy']
    age                   = data['Age']
    gender                = data['Gender']
    lineupSize            = _copy.copy(participantId)

    lineupSize[:] = 1
    targetLineup.replace({"Target":"targetPresent","Lure":"targetAbsent"}, inplace=True)
    responseType.replace({"Lure":"rejectId", "Target":"suspectId"}, inplace=True)

    dataNew = _pandas.DataFrame()
    dataNew['participantId'] = participantId
    dataNew['lineupSize']    = lineupSize
    dataNew['targetLineup']  = targetLineup
    dataNew['responseType']  = responseType
    dataNew['confidence']    = confidence
    dataNew['age']           = age
    dataNew['gender']       = gender

    dataNew.to_csv("test3.csv")

def makeTestXlsx() :
    pass

    
