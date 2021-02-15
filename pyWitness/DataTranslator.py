import pandas as _pandas
import numpy as _np
from .DataRaw import DataRaw

def relabelConfidenceForShowups(df) :
    pass

def published_Aken_2020_Experiment1(fileName = "experiment1", excelSheet = 'E1') :
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

