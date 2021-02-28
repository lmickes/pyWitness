import pandas as _pandas
import numpy as _np
import copy as _copy
from .DataRaw import DataRaw

def relabelConfidenceForShowups(df) :
    conf_min = df["confidence"][1] -df["confidence"][0]
    df["confidence"][_np.logical_and(df["lineupSize"] == 1, df["responseType"] == "rejectId")] = -df["confidence"] - conf_min

    df["responseType"][_np.logical_and(_np.logical_and(df["responseType"] == "fillerId", df["targetLineup"] == "targetAbsent"), df["lineupSize"]==1)] = "suspectId"

def published_Wilson_2018_Experiment12(fileName = "Wilson_SealeCarlisle_Mickes2017.xlsx", excelSheet = "Exp1_2") :

    # load spreadsheet
    data = _pandas.read_excel(fileName, excelSheet, engine='openpyxl')

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

    return dr

def published_Wilson_2018_Experiment34(fileName = "Wilson_SealeCarlisle_Mickes2017.xlsx", excelSheet = "Exp3") :
    data = _pandas.read_excel(fileName, excelSheet, engine='openpyxl')

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

    return dr

def published_Akan_2020_Experiment1(fileName = "experiment1", excelSheet = 'E1') :
    data = _pandas.read_excel(fileName, excelSheet, engine='openpyxl')

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

    return dr

