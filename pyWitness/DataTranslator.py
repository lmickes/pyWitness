import pandas as _pandas
import numpy as _np
import copy as _copy
import os as _os
import sys as _sys

from .DataRaw import DataRaw
from .DataRaw import dataMapSdtlu

_dir = _os.path.dirname(__file__)

def relabelConfidenceForShowups(df) :
    conf_min = df["confidence"][1] -df["confidence"][0]
    df["confidence"][_np.logical_and(df["lineupSize"] == 1, df["responseType"] == "rejectId")] = -df["confidence"] - conf_min

    df["responseType"][_np.logical_and(_np.logical_and(df["responseType"] == "fillerId", df["targetLineup"] == "targetAbsent"), df["lineupSize"]==1)] = "suspectId"

def openExcelFile(fileName, excelSheet) :

    try :
        d = _pandas.read_excel(fileName, excelSheet, engine='openpyxl')
        return d
    except KeyError :
        print("Excel file does not have sheet called :"+excelSheet)

def openCsvFile(fileName) :

    d = _pandas.read_csv(fileName)
    return d

#########################################################################################################
def published_Colloff_2016(fileName = "", excelSheet = "Data") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2016_ColloffWadeStrange/Colloff_Wade_Strange2016.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['subjectNo ']
    targetLineup        = data['targetLabel ']
    lineupSize          = _copy.copy(data['targetLabel '])
    responseType        = _copy.copy(data['targetLabel '])
    confidence          = data['confidenceRounded']

    targetLineup.replace({"absent":"targetAbsent", "present":"targetPresent"}, inplace=True)
    lineupSize.loc[:]   = 6

    face0               = data['face0 ']
    face1               = data['face1 ']
    face2               = data['face2 ']
    face3               = data['face3 ']
    face4               = data['face4 ']
    face5               = data['face5 ']
    faceSelected        = data['faceSelected ']

    for i in range(0,len(faceSelected)) : 
        if faceSelected[i] == "notpresent" : 
            responseType[i] = "rejectId"
        elif faceSelected[i] == "face0div" and face0[i].find("perpetrator") != -1 :
            responseType[i] = "suspectId"
        elif faceSelected[i] == "face1div" and face1[i].find("perpetrator") != -1 :
            responseType[i] = "suspectId"
        elif faceSelected[i] == "face2div" and face2[i].find("perpetrator") != -1 :
            responseType[i] = "suspectId"
        elif faceSelected[i] == "face3div" and face3[i].find("perpetrator") != -1 :
            responseType[i] = "suspectId"
        elif faceSelected[i] == "face4div" and face4[i].find("perpetrator") != -1 :
            responseType[i] = "suspectId"
        elif faceSelected[i] == "face5div" and face5[i].find("perpetrator") != -1 :
            responseType[i] = "suspectId"
        else : 
            responseType[i] = "fillerId"

    # get other data
    treatmentLabel          = data['treatmentLabel ']
    exclude                 = data['exclude']


    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(treatmentLabel   = treatmentLabel)
    dataNew = dataNew.assign(exclude          = exclude)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

    #########################################################################################################
def published_SealeCarlisle_Colloff_Flowe_etal_2019(fileName = "", excelSheet = "Study 1 Laboratory Data") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_Seale-CarlisleColloffFloweWellsWixtedMickes/Seale-Carlisle_et_al_raw_data.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['Participant Number']
    targetLineup        = data['Target Absent or Target Present']
    lineupSize          = _copy.copy(data['Participant Number'])
    responseType        = data['Said Absent or Said Present']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target Absent":"targetAbsent", "Target Present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said Present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said Absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said Present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said Present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said Absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    exclude                       = data['Validation Accuracy']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(exclude          = exclude)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr      

#########################################################################################################
def published_SealeCarlisle_Mickes_2016(fileName = "", excelSheet = "data") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2016_SealeCarlisle_Mickes/USvUKdata.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['Subject #']
    targetLineup        = data['Target Absent (2) or Present (1)']
    lineupSize          = _copy.copy(data['UK (1) US (2)'])
    condition           = data['UK (1) US (2)']
    responseType        = data['Said Absent or Present']
    confidence          = data['Confidence 1']
    accuracy            = data['Which One Accuracy 1']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.replace({"US":6, "UK":9}, inplace=True)
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    exclude                       = data['Validation Question Correct']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)
    dataNew = dataNew.assign(exclude          = exclude)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

#########################################################################################################
def published_SealeCarlisle_Wetmore_Flowe_Mickes_2019_E1(fileName = "", excelSheet = "E1") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_SealeCarlisleWetmoreFloweMickes/ESRC_Data_Archive.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['ID number']
    targetLineup        = data['Target-Present or Target-Absent']
    lineupSize          = _copy.copy(data['ID number'])
    responseType        = data['Participant Target-Present or Target-absent']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 9
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said-present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said-absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said-present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition                      = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

def published_SealeCarlisle_Wetmore_Flowe_Mickes_2019_E2(fileName = "", excelSheet = "E2") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_SealeCarlisleWetmoreFloweMickes/ESRC_Data_Archive.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['ID number']
    targetLineup        = data['Target-Present or Target-Absent']
    lineupSize          = _copy.copy(data['ID number'])
    responseType        = data['Participant Target-Present or Target-absent']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 9
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said-present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said-absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said-present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition                      = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

def published_SealeCarlisle_Wetmore_Flowe_Mickes_2019_E3a(fileName = "", excelSheet = "E3a") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_SealeCarlisleWetmoreFloweMickes/ESRC_Data_Archive.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['ID number']
    targetLineup        = data['Target-Present or Target-Absent']
    lineupSize          = _copy.copy(data['ID number'])
    responseType        = data['Participant Target-Present or Target-absent']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 9
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said-present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said-absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said-present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition                      = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

def published_SealeCarlisle_Wetmore_Flowe_Mickes_2019_E3b(fileName = "", excelSheet = "E3b") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_SealeCarlisleWetmoreFloweMickes/ESRC_Data_Archive.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['ID number']
    targetLineup        = data['Target-Present or Target-Absent']
    lineupSize          = _copy.copy(data['ID number'])
    responseType        = data['Participant Target-Present or Target-absent']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 9
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said-present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said-absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said-present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition                      = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

def published_SealeCarlisle_Wetmore_Flowe_Mickes_2019_E4(fileName = "", excelSheet = "E4") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_SealeCarlisleWetmoreFloweMickes/ESRC_Data_Archive.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['ID number']
    targetLineup        = data['Target-Present or Target-Absent']
    lineupSize          = _copy.copy(data['ID number'])
    responseType        = data['Participant Target-Present or Target-absent']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.replace({"6-member":6, "9-member":9}, inplace=True)
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said-present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said-absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said-present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition                      = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

def published_SealeCarlisle_Wetmore_Flowe_Mickes_2019_E5(fileName = "", excelSheet = "E5") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_SealeCarlisleWetmoreFloweMickes/ESRC_Data_Archive.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId       = data['ID number']
    targetLineup        = data['Target-Present or Target-Absent']
    lineupSize          = _copy.copy(data['ID number'])
    responseType        = data['Participant Target-Present or Target-absent']
    confidence          = data['Confidence']
    accuracy            = data['Accuracy']

    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.replace({"6-member":6, "9-member":9}, inplace=True)
   
    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "Said-present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "Said-absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "Said-present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "Said-absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition                      = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr       

#########################################################################################################

def published_Colloff_SealeCarlisle_Karoğlu_etal2020_E1(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_SealeCarlisle_Karoğlu_etal/Exp1_Data.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    targetLineup     = data['targetPresentRaw']
    lineupSize       = _copy.copy(data['videoRaw'])   # copy column
    accuracy         = data['accuracy']
    response         = data['participantTargetPresent']
    responseType     = _copy.copy(data['videoRaw'])   # copy column
    confidence       = data['confidence']

    # translate data
    targetLineup.replace({"Target Absent":"targetAbsent", "Target Present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 9

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == 1)
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == 0)
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 1)
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == 1)
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 0)

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition        = data['condition']
    age              = data['age']
    gender           = data['sex']
    ethnicity        = data['ethnicity']
    keep             = data['keep']
    
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)

    dataNew = dataNew.assign(condition        = condition)
    dataNew = dataNew.assign(age              = age)
    dataNew = dataNew.assign(gender           = gender)
    dataNew = dataNew.assign(ethnicity        = ethnicity)
    dataNew = dataNew.assign(keep             = keep)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

def published_Colloff_SealeCarlisle_Karoğlu_etal2020_E2(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_SealeCarlisle_Karoğlu_etal/Exp2_Data.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['ParticipantId']
    targetLineup     = data['TargetPresent']
    lineupSize       = _copy.copy(data['Age'])   # copy column
    accuracy         = data['Accuracy']
    response         = data['ParticipantTargetPresent']
    responseType     = _copy.copy(data['Age'])   # copy column
    confidence       = data['Confidence']

    # translate data
    targetLineup.replace({0:"targetAbsent", 1:"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == "yes")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == "no")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "yes")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == "yes")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "no")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition        = data['EncodingConditionRaw']
    age              = data['Age']
    gender           = data['Sex']
    ethnicity        = data['Ethnicity']
    
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(accuracy         = accuracy)
    dataNew = dataNew.assign(response         = response)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)

    dataNew = dataNew.assign(condition        = condition)
    dataNew = dataNew.assign(age              = age)
    dataNew = dataNew.assign(gender           = gender)
    dataNew = dataNew.assign(ethnicity        = ethnicity)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################   

def published_Colloff_Flowe_Smith_etal_2020_E1(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Flowe_Smith_etal/Exp1_osf_data_CodeBook.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    targetLineup     = data['TargetPresent']
    lineupSize       = _copy.copy(data['ExperimentId'])   # copy column
    accuracy         = data['Correct']
    responseType     = data['SaidAbsentorPresent']
    confidence       = data['Confidence']

    # translate data
    targetLineup.replace({"no":"targetAbsent", "yes":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == 'present')
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == 'absent')
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == 'present')
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == 'present')
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == 'absent')

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    ownRace          = data['OwnRace']
    lineupCat        = data['LineupType']
    age              = data['Age']
    gender           = data['SexId']
    ethnicity        = data['EthnicityId']
    include          = data['Include']
    
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = daata.New.assign(accuracy       = accuracy)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)

    dataNew = dataNew.assign(condition        = condition)
    dataNew = dataNew.assign(age              = age)
    dataNew = dataNew.assign(gender           = gender)
    dataNew = dataNew.assign(ethnicity        = ethnicity)
    dataNew = dataNew.assign(keep             = keep)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_Morgan_2019(fileName = "", excelSheet = "Raw Data") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2019_Morgan_Tamminen_SealeCarlisle_Mickes/2019_Morgan_Tamminen_SealeCarlisle_Mickes.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId    = data['Participant ID']
    targetLineup     = data['Target Present or Target Absent Lineup']
    lineupSize       = _copy.copy(data['Minutes2'])   # copy column
    accuracy         = data['Accuracy']
    response         = data['Participant Response']
    responseType     = _copy.copy(data['Target Present or Target Absent Lineup'])   # copy column
    confidence       = data['Confidence']

    # translate data
    targetLineup.replace({"Target Absent":"targetAbsent", "Target Present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    response.replace({"absent":"targetAbsent", "present":"targetPresent"}, inplace=True)

    accuracy.replace({"Incorrect":"incorrect"}, inplace=True)

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == "incorrect"),response == "targetPresent")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == "correct"),response == "targetAbsent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == "incorrect"),response == "targetPresent")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == "correct"),response == "targetPresent")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == "incorrect"),response == "targetAbsent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age              = data['Age']
    gender           = data['Sex']
    condition        = data['Condition']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(age              = age)
    dataNew = dataNew.assign(gender           = gender)
    dataNew = dataNew.assign(condition        = condition)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_Wilson_2018_Experiment12(fileName = "", excelSheet = "Exp1_2") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2017_Wilson_SealeCarlisle_Mickes/Wilson_SealeCarlisle_Mickes2017.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId    = data['ID #']
    targetLineup     = data['Target Absent or Present']
    lineupSize       = _copy.copy(data['Present or Absent Response'])   # copy column
    accuracy         = data['Accuracy']
    response         = data['Present or Absent Response']
    responseType     = _copy.copy(data['Present or Absent Response'])   # copy column
    confidence       = data['Confidence']

    # translate data
    targetLineup.replace({"Target-absent":"targetAbsent", "Target-present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == "Present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == "Absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "Present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == "Present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "Absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    experiment       = data['Exp']
    age              = data['Age']
    gender           = data['Gender']
    group            = data['Group']
    description      = data['Description']
    previouslyViewed = data['Previously Viewed Video']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)
    dataNew = dataNew.assign(experiment       = experiment)
    dataNew = dataNew.assign(age              = age)
    dataNew = dataNew.assign(gender           = gender)
    dataNew = dataNew.assign(group            = group)
    dataNew = dataNew.assign(description      = description)
    dataNew = dataNew.assign(previouslyViewed = previouslyViewed)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

def published_Wilson_2018_Experiment34(fileName = "", excelSheet = "Exp3") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2017_Wilson_SealeCarlisle_Mickes/Wilson_SealeCarlisle_Mickes2017.xlsx"

    data = openExcelFile(fileName, excelSheet)

    group         = data['Group']
    targetLineup  = data['Target or Lure']
    responseType  = data['Target or Lure Response']
    confidence    = data['Confidence']
    lineupSize    = _copy.copy(data['Confidence'])   # copy column

    description   = data['Description']
    age           = data['Age']
    gender        = data['Gender']

    targetLineup.replace({"Target":"targetPresent","Lure":"targetAbsent"}, inplace=True)
    responseType.replace({"Lure":"rejectId", "Target":"suspectId"}, inplace=True)
    lineupSize[:] = 1

    dataNew = _pandas.DataFrame()
    # dataNew = dataNew.assign(participantId = participantId)
    dataNew = dataNew.assign(targetLineup  = targetLineup)
    dataNew = dataNew.assign(lineupSize    = lineupSize)
    dataNew = dataNew.assign(responseType  = responseType)
    dataNew = dataNew.assign(confidence    = confidence)

    dataNew = dataNew.assign(group         = group)
    dataNew = dataNew.assign(description   = description)
    dataNew = dataNew.assign(age           = age)
    dataNew = dataNew.assign(gender        = gender)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################
def published_Horry_Fitzgerald_Mansour_2020(fileName = "", excelSheet = 'Sheet1') :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Horry_Fitzgerald_Mansour/Final dataset.xlsx"

    data = openExcelFile(fileName, excelSheet)

    participantId = data['Participant']
    targPresence  = data['TargPresence']
    targetLineup  = _copy.copy(data['TargPresence'])
    lineupType    = data['LineupType']
    lineupSize    = _copy.copy(data['Site'])
    responseType  = _copy.copy(data['LabOnline'])
    confidence    = data['ConfBin']
    targetLineup[targPresence > 0] = 'targetPresent'
    targetLineup[targPresence < 1] = 'targetAbsent'

    susID         = data['SusID']
    fillerID      = data['FillerID']
    nonID         = data['NonID']

    responseType[susID >0]    = "suspectId"
    responseType[fillerID >0] = "fillerId"
    responseType[nonID >0]    = "rejectId"
    lineupSize[:] = 6


    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId = participantId)
    dataNew = dataNew.assign(targetLineup  = targetLineup)
    dataNew = dataNew.assign(lineupType    = lineupType)
    dataNew = dataNew.assign(lineupSize    = lineupSize)
    dataNew = dataNew.assign(responseType  = responseType)
    dataNew = dataNew.assign(confidence    = confidence)


    # show up confidence
    relabelConfidenceForShowups(dataNew)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr
#########################################################################################################
def published_Akan_2020_Experiment1(fileName = "", excelSheet = 'E1') :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Akan/Experiment1.xlsx"

    data = openExcelFile(fileName, excelSheet)

    participantId = data['Subject #']
    targetLineup  = data['TP/TA']
    condition     = data['Condition']
    lineupSize    = data['Condition']
    responseType  = data['Response']
    confidence    = data['Confidence']

    targetLineup.replace({1:"targetPresent", 2:"targetAbsent"}, inplace=True)

    responseType.replace({192:"suspectId", "Perpetrator is Not Present":"rejectId"}, inplace=True)
    responseType.loc[_np.logical_and(responseType != "rejectId", responseType != "suspectId")] = "fillerId"     # this is why the naive translator does not work

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId = participantId)
    dataNew = dataNew.assign(targetLineup  = targetLineup)
    dataNew = dataNew.assign(condition     = condition)
    dataNew = dataNew.assign(lineupSize    = lineupSize)
    dataNew = dataNew.assign(responseType  = responseType)
    dataNew = dataNew.assign(confidence    = confidence)

    # show up confidence
    relabelConfidenceForShowups(dataNew)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################
def published_Cohens_2020_Gronlund() :
    fileName = _dir + "/../data/published/2020_CohensStarnsRotello/gronlund_data.csv"
    dr       = DataRaw(fileName,dataMapping=dataMapSdtlu)

    c = _np.logical_and(dr.data['targetLineup'] == "targetAbsent", dr.data['responseType'] == "suspectId")
    dr.data['responseType'][c] = "fillerId"

    return dr

def published_Cohens_2020_Palmer() :
    fileName = _dir + "/../data/published/2020_CohensStarnsRotello/palmer_data.csv"
    dr       = DataRaw(fileName,dataMapping=dataMapSdtlu)

    c = _np.logical_and(dr.data['targetLineup'] == "targetAbsent", dr.data['responseType'] == "suspectId")
    dr.data['responseType'][c] = "fillerId"

    return dr

def published_Cohens_2020_PalmerDelayShort() :
    fileName = _dir + "/../data/published/2020_CohensStarnsRotello/palmer_delay_short_data.csv"
    dr       = DataRaw(fileName,dataMapping=dataMapSdtlu)

    c = _np.logical_and(dr.data['targetLineup'] == "targetAbsent", dr.data['responseType'] == "suspectId")
    dr.data['responseType'][c] = "fillerId"

    return dr

def published_Cohens_2020_PalmerDelayLong() :
    fileName = _dir + "/../data/published/2020_CohensStarnsRotello/palmer_delay_long_data.csv"
    dr       = DataRaw(fileName,dataMapping=dataMapSdtlu)

    c = _np.logical_and(dr.data['targetLineup'] == "targetAbsent", dr.data['responseType'] == "suspectId")
    dr.data['responseType'][c] = "fillerId"

    return dr

    #########################################################################################################
def published_Jalava_Smith_Mackovichova_2021_1(fileName = "", excelSheet = 'EXP 1A') :

    raise Exception("this doesn't work")
    if fileName == "" :
        fileName = _dir+"/../data/published/2021_Jalava_Smith_Mackovichova/NSO_EXP1A_EXP1B_Data.xlsx"

    data = openExcelFile(fileName, excelSheet)

    participantId = data['Participant']
    targetLineup  = data['Target Presence']
    responseType  = data['Response']
    lineupSize    = _copy.copy(data['Participant'])
    confidence    = _copy.copy(data['Participant'])

    responseOptionCondition = data['Response Option Condition']
    qualityOfView           = data['Quality of View']
    confidence01            = data['Please use the slider to indicate on a scale from 0% (not at all) to 100% (completely), how confident you are in your identification decision. - Confidence %:']
    confidence2             = data['Please use the slider to indicate on a scale from 0% (not at all) to 100% (completely), how confident you would have been in your YES or NO decision. - Confidence %:']
    notSureResponseType     = data['If we had not given you the option to respond NOT SURE when making your identification decision, what response would you have chosen?']

    lineupSize[:] = 1
    targetLineup.replace({0:"targetAbsent", 1:"targetPresent"}, inplace=True)
    responseType.replace({0:"rejectId", 1:"suspectId", 2:"notSure"}, inplace=True)

    responseType[notSureResponseType == "NO"]  = 'rejectId'
    responseType[notSureResponseType == "YES"] = 'suspectId'

    confidence              =  _copy.copy(confidence01)

    c0   = reponseType == 'rejectId' 
    c2NO = _np.logical_and(responeType == 'notSure', notSureResponseType == 'NO')

    confidence[_np.isnan(confidence01)] = confidence2[_np.isnan(confidence01)]

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId = participantId)
    dataNew = dataNew.assign(targetLineup  = targetLineup)
    dataNew = dataNew.assign(lineupSize    = lineupSize)
    dataNew = dataNew.assign(responseType  = responseType)
    dataNew = dataNew.assign(confidence    = confidence)

    # show up confidence
    # relabelConfidenceForShowups(dataNew)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

    
#########################################################################################################

def published_Colloff_Flowe_SealeCarlisle_2020_Experiment1(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Flowe_SealeCarlisle_etal/Exp1_Data.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = _copy.copy(data['videoRaw'])
    targetLineup     = data['targetPresentRaw']
    lineupSize       = _copy.copy(data['videoRaw'])   # copy column
    accuracy         = data['accuracy']
    response         = data['participantTargetPresent']
    responseType     = _copy.copy(data['videoRaw'])   # copy column
    confidence       = data['confidence']

    # translate data
    targetLineup.replace({"Target Absent":"targetAbsent", "Target Present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 9

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == 1)
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == 0)
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 1)
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == 1)
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 0)

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    condition        = data['condition']
    age              = data['age']
    gender           = data['sex']
    ethnicity        = data['ethnicity']
    keep             = data['keep']
    
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId    = participantId)
    dataNew = dataNew.assign(targetLineup     = targetLineup)
    dataNew = dataNew.assign(lineupSize       = lineupSize)
    dataNew = dataNew.assign(responseType     = responseType)
    dataNew = dataNew.assign(confidence       = confidence)

    dataNew = dataNew.assign(condition        = condition)
    dataNew = dataNew.assign(age              = age)
    dataNew = dataNew.assign(gender           = gender)
    dataNew = dataNew.assign(ethnicity        = ethnicity)
    dataNew = dataNew.assign(keep             = keep)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_Colloff_Flowe_SealeCarlisle_2020_Experiment2(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Flowe_SealeCarlisle_etal/Exp2_Data.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['ParticipantId']
    targetLineup     = data['TargetPresent']
    lineupSize       = _copy.copy(data['Interactors'])   # copy column
    accuracy         = data['Accuracy']
    response         = data['ParticipantTargetPresent']
    responseType     = data['ParticipantSelection']
    confidence       = data['Confidence']

    # translate data
    targetLineup.replace({0:"targetAbsent", 1:"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType  == "filler")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "reject")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType  == "filler")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType  == "target")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType  == "reject")

    responseType.loc[taFillerId]    = "fillerId"
    responseType.loc[taRejectId]    = "rejectId"
    responseType.loc[tpFillerId]    = "fillerId"
    responseType.loc[tpSuspectId]   = "suspectId"
    responseType.loc[tpRejectId]    = "rejectId"

    # get other data
    age                             = data['Age']
    gender                          = data['Sex']
    ethnicity                       = data['Ethnicity']
    encodingConditionRaw            = data['EncodingConditionRaw']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId          = participantId)
    dataNew = dataNew.assign(targetLineup           = targetLineup)
    dataNew = dataNew.assign(lineupSize             = lineupSize)
    dataNew = dataNew.assign(responseType           = responseType)
    dataNew = dataNew.assign(confidence             = confidence)

    dataNew = dataNew.assign(age                    = age)
    dataNew = dataNew.assign(gender                 = gender)
    dataNew = dataNew.assign(ethnicity              = ethnicity)
    dataNew = dataNew.assign(encodingConditionRaw   = encodingConditionRaw)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_Colloff_Flowe_Winsor_2020(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Flowe_Winsor_etal/OpenAccessData.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['SubjectId']
    targetLineup     = data['TargetPresent']
    lineupSize       = _copy.copy(data['Age'])   # copy column
    accuracy         = data['Correct']
    response         = data['SaidAbsentorPresent']
    responseType     = data['IDResponse']   
    confidence       = data['Confidence']

    # translate data
    targetLineup.replace({"no":"targetAbsent", "yes":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),responseType == "foil")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),responseType == "reject")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "foil")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),responseType == "perpetrator")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),responseType == "reject")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['Age']
    gender                = data['Gender']
    ethnicity             = data['Ethnicity']
    includeFinalSample    = data['IncludeFinalSample']
    ageGroup              = data['AgeGroup']

    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)

    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)
    dataNew = dataNew.assign(ethnicity                      = ethnicity)
    dataNew = dataNew.assign(includeFinalSample             = includeFinalSample)
    dataNew = dataNew.assign(ageGroup                       = ageGroup)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_Colloff_Wilson_SealeCarlisle_Wixted_2020_Experiment1(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Wilson_SealeCarlisle_Wixted/Experiment1.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['idnumber']
    targetLineup     = data['targetPresent']
    lineupSize       = _copy.copy(data['idnumber'])   # copy column
    accuracy         = data['accuracy']
    response         = data['participantTargetPresent']
    responseType     = data['participantIDdecision']   
    confidence       = data['confidence']

    # translate data
    targetLineup.replace({0:"targetAbsent", 1:"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == 1)
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == 0)
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 1)
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == 1)
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 0)

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['age']
    gender                = data['gender']
    ethnicity             = data['ethnicity']
    include               = data['include']
 
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)

    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)
    dataNew = dataNew.assign(ethnicity                      = ethnicity)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_Colloff_Wilson_SealeCarlisle_Wixted_2020_Exp2(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Wilson_SealeCarlisle_Wixted/Experiment2.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['idnumber']
    targetLineup     = data['targetPresent']
    lineupSize       = _copy.copy(data['idnumber'])   # copy column
    accuracy         = data['accuracy']
    response         = data['participantTargetPresent']
    responseType     = data['participantIDdecision']   
    confidence       = data['confidence']

    # translate data
    targetLineup.replace({0:"targetAbsent", 1:"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == 1)
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == 0)
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 1)
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == 1)
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == 0)

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['age']
    gender                = data['gender']
    ethnicity             = data['ethnicity']
    include               = data['include']
 
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)

    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)
    dataNew = dataNew.assign(ethnicity                      = ethnicity)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_2020_Colloff_Wixted_Exp1(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Wixted/Colloff_Wixted_Exp1.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['subjectNo ']
    targetLineup     = data['targetLabel ']
    lineupSize       = _copy.copy(data['subjectNo '])   # copy column
    accuracy         = data['correct']
    response         = data['SaidAbsentOrPresent']
    responseType     = _copy.copy(data['SaidAbsentOrPresent']) 
    confidence       = data['confidence ']

    # translate data
    targetLineup.replace({"absent":"targetAbsent", "present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == "Present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == "Absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "Present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == "Present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "Absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['age']
    gender                = data['Gender']
    ethnicity             = data['Ethnicity']
    treatmentLabel        = data['treatmentLabel ']
    include               = data['include']
 
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(response                       = response)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)

    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)
    dataNew = dataNew.assign(ethnicity                      = ethnicity)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

def published_2020_Colloff_Wixted_Exp2(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Wixted/Colloff_Wixted_Exp2.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['subjectID']
    targetLineup     = data['targetLabel ']
    lineupSize       = _copy.copy(data['subjectID'])   # copy column
    accuracy         = data['correct']
    response         = data['SaidAbsentOrPresent']
    responseType     = _copy.copy(data['SaidAbsentOrPresent']) 
    confidence       = data['confidence ']

    # translate data
    targetLineup.replace({"absent":"targetAbsent", "present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),response == "Present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),response == "Absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "Present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),response == "Present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),response == "Absent")

    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['age']
    gender                = data['Gender']
    ethnicity             = data['Ethnicity']
    treatmentLabel        = data['treatmentLabel ']
    include               = data['include']
 
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(response                       = response)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)

    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)
    dataNew = dataNew.assign(ethnicity                      = ethnicity)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

def published_2020_Colloff_Wixted_Exp3(fileName = "") :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Colloff_Wixted/Colloff_Wixted_Exp3.csv"

    # load spreadsheet
    data = openCsvFile(fileName)

    # get important data
    participantId    = data['subjectID']
    targetLineup     = data['targetLabel ']
    lineupSize       = _copy.copy(data['subjectID'])   # copy column
    accuracy         = data['correct']
    response         = data['SaidAbsentOrPresent']
    responseType     = _copy.copy(data['SaidAbsentOrPresent']) 
    confidence       = data['confidence ']

    # translate data
    targetLineup.replace({"absent":"targetAbsent", "present":"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  _np.logical_or(accuracy == '0', accuracy == "filler")),response == "Present")
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == '1'),response == "Absent")
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == '0'),response == "Present")
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == '1'),response == "Present")
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == '0'),response == "Absent")
   
    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['age']
    gender                = data['Gender']
    ethnicity             = data['Ethnicity']
    treatmentLabel        = data['treatmentLabel ']
    include               = data['include']
 
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(response                       = response)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)

    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)
    dataNew = dataNew.assign(ethnicity                      = ethnicity)

    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################

def published_2020_Lucas_etal_Exp1(fileName = "", excelSheet = 'Exp 1 Data') :

    if fileName == "" :
        fileName = _dir+"/../data/published/2020_Lucas_Brewer_Michael_etal/DataResponseOptionExps.xlsx"

    # load spreadsheet
    data = openExcelFile(fileName, excelSheet)

    # get important data
    participantId    = data['ID']
    targetLineup     = data['Presence']
    lineupSize       = _copy.copy(data['ID'])   # copy column
    accuracy         = data['Accuracy']
    decision         = data['Decision']
    responseType     = _copy.copy(data['ID'])   # copy column
    confidence       = data['Confidence']


    # translate data
    targetLineup.replace({0:"targetAbsent", 1:"targetPresent"}, inplace=True)
    lineupSize.loc[:] = 6

    taFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 0),decision == 2)
    taRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetAbsent",  accuracy == 1),decision == 0)
    tpFillerId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),decision == 2)
    tpSuspectId      = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 1),decision == 1)
    tpRejectId       = _np.logical_and(_np.logical_and(targetLineup == "targetPresent", accuracy == 0),decision == 0)
   
    responseType.loc[taFillerId]  = "fillerId"
    responseType.loc[taRejectId]  = "rejectId"
    responseType.loc[tpFillerId]  = "fillerId"
    responseType.loc[tpSuspectId] = "suspectId"
    responseType.loc[tpRejectId]  = "rejectId"

    # get other data
    age                   = data['Age']
    gender                = data['Sex']
 
    dataNew = _pandas.DataFrame()
    dataNew = dataNew.assign(participantId                  = participantId)
    dataNew = dataNew.assign(targetLineup                   = targetLineup)
    dataNew = dataNew.assign(lineupSize                     = lineupSize)
    dataNew = dataNew.assign(responseType                   = responseType)
    dataNew = dataNew.assign(confidence                     = confidence)
    dataNew = dataNew.assign(age                            = age)
    dataNew = dataNew.assign(gender                         = gender)


    dr = DataRaw('')
    dr.data = dataNew
    dr.checkData()

    return dr

#########################################################################################################
