import pandas as _pandas

def makeTest1Csv(lineupSize = 6) :
    data     = _pandas.read_excel('Seale-Carlisle_et_al_raw_data.xlsx',
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

def makeTest2Csv() :
    pass


def makeTestXlsx() :
    pass

    
