import csv
import math
import random
import scipy.stats

rowTable = []
learnTable = []
testTable = []
dt = {}
baseTable = []
kCrossValidation = []
accuracy = 0

#======================================================
def readFileToThresholds(workFile, thresholdsQty):
    minInAttribute = [100000000] * 58
    maxInAttribute = [0] * 58
    thresholdStep = [0] * 58
    spamCounter = 0
    numOfInstance = 0
    # --------------------------------------------------------------------------------------------
    # Read file into table
    # while reading, 1. change to Float and keep Min & Max for each attribute 2. sum coll(57) "1' for H(S)
    fileReader = csv.reader(open(workFile, newline=''), delimiter=',', quotechar='|')
    for row in fileReader:
        attQty = len(row) - 1
        baseTable.insert(numOfInstance, row)
        for attIndx in range(attQty+1):
            baseTable[numOfInstance][attIndx] = float(baseTable[numOfInstance][attIndx])
            if row[attIndx] < minInAttribute[attIndx]:
                minInAttribute[attIndx] = row[attIndx]
            if row[attIndx] > maxInAttribute[attIndx]:
                maxInAttribute[attIndx] = row[attIndx]
        numOfInstance += 1
        spamCounter += row[attQty]
    for attIndx in range(attQty):
        thresholdStep[attIndx] = (maxInAttribute[attIndx] - minInAttribute[
            attIndx]) / thresholdsQty  # calculate step for each attribute
    # -----------------------------------------------------------------------
    #change each attribute to "thresholdsQty" thresholds using the Min & Max vectors
    #print("len 4:", len(rowTable), "numOfInstance:", numOfInstance)
    for ins in range(numOfInstance):
        for att in range(attQty):  # only 57 to leave spam 0/1 as is
            #print("baseTable[ins][att]:", baseTable[ins][att])
            #print("rowTable[ins][att]:", rowTable[ins][att])
            #print("thresholdStep[att]:", thresholdStep[att])
            baseTable[ins][att] = int(rowTable[ins][att] / thresholdStep[att])
            if baseTable[ins][att] == thresholdsQty:
                baseTable[ins][att] += -1
        baseTable[ins].insert(attQty, int(rowTable[ins][attQty]))
    """
    print("Min:", minInAttribute)
    print("Max:", maxInAttribute)
    print("=======================")
    print('numOfInstance:', numOfInstance)
    print("spam:", int(spamCounter))
    print("entropy:", entropy)
    for i in range(numOfInstance):
       print("fromRow:", i, rowTable[i])
    
    for i in range(len(baseTable)):
       print("baseTable:", i, baseTable[i])
    """

#======================================================================
def readFile(workFile, thresholdsQty, ratio):
    minInAttribute = [100000000] * 58
    maxInAttribute = [0] * 58
    thresholdStep = [0] * 58
    spamCounter = 0
    numOfInstance = 0
    learnQty = 0
    testQty = 0
    # --------------------------------------------------------------------------------------------
    # Read file into table
    # while reading, 1. change to Float and keep Min & Max for each attribute 2. sum coll(57) "1' for H(S)
    fileReader = csv.reader(open(workFile, newline=''), delimiter=',', quotechar='|')
    for row in fileReader:
        attQty = len(row) - 1
        rowTable.insert(numOfInstance, row)
        for attIndx in range(attQty + 1):
            rowTable[numOfInstance][attIndx] = float(rowTable[numOfInstance][attIndx])
            if row[attIndx] < minInAttribute[attIndx]:
                minInAttribute[attIndx] = row[attIndx]
            if row[attIndx] > maxInAttribute[attIndx]:
                maxInAttribute[attIndx] = row[attIndx]
        numOfInstance += 1
        spamCounter += row[attQty]
    for attIndx in range(attQty):
        thresholdStep[attIndx] = (maxInAttribute[attIndx] - minInAttribute[
            attIndx]) / thresholdsQty  # calculate step for each attribute
    # -----------------------------------------------------------------------
    # Split to "learnTable" and "testTable" using "ratio"
    # While splitting, change each attribute to "thresholdsQty" thresholds using the Min & Max vectors
    for ins in range(numOfInstance):
        takeThisInctance = random.randint(1, 100)
        if takeThisInctance < ratio:
            learnTable.append([])
            for att in range(attQty):  # only 57 to leave spam 0/1 as is
                learnTable[learnQty].insert(att, int(rowTable[ins][att] / thresholdStep[att]))
                if learnTable[learnQty][att] == thresholdsQty:
                    learnTable[learnQty][att] += -1
            learnTable[learnQty].insert(attQty, int(rowTable[ins][attQty]))
            learnQty += 1
        else:
            testTable.append([])
            for att in range(attQty):  # only 57 to leave spam 0/1 as is
                testTable[testQty].insert(att, int(rowTable[ins][att] / thresholdStep[att]))
                if testTable[testQty][att] == thresholdsQty:
                    testTable[testQty][att] += -1
            testTable[testQty].insert(attQty, int(rowTable[ins][attQty]))
            testQty += 1
        entropy = -spamCounter / numOfInstance * math.log(spamCounter / numOfInstance, 2) \
            - ((numOfInstance - spamCounter) / numOfInstance) * (
                  math.log((numOfInstance - spamCounter) / numOfInstance, 2))
        """
        print("Min:", minInAttribute)
        print("Max:", maxInAttribute)
        print("=======================")
        print('numOfInstance:', numOfInstance)
        print("spam:", int(spamCounter))
        print("entropy:", entropy)
        for i in range(numOfInstance):
        print("fromRow:", i, rowTable[i])
        
        for i in range(learnQty):
            print("learnTable:", i, learnTable[i])
        """
    return [learnTable, learnQty, testTable, testQty, entropy, attQty]

# ====================================================================
def root(learnTable, learnTableSize, treshQty, attOpenList):
    # ----------------------------------------------------------------------------------------------
    # 1. run on "learn" table and creates 3D "infoArray" that accumulates Y/N spame to attributeQty X thresholdsQty X 5
    bestAtt = [666, 666, 666]
    thisLearnTableCut = 0
    #print("root", len(learnTable), learnTableSize)
    # ----------------------------------------------------------------------------------------------
    # 1. run on "learn" table and creates 3D "infoArray" that accumulates Y/N spame to attributeQty X thresholdsQty X 5
    infoArray = [[[0 for k in range(8)] for j in range(treshQty)] for i in
                 range(len(attOpenList))]
    #print(infoArray)
    for ins in range(learnTableSize):  # learnTable[0] contains header 1..attQty, so we start from ins+1
        #print("learnTable[ins]:", ins, learnTable[ins])
        # --------- If the line in LearnTable meets criteria, update InfoArray ------------
        for att in (attOpenList):
            #print("test ins:", ins, "att:", att, "infoArray[att][learnTable[ins][att]][0]",
            #      infoArray[att][learnTable[ins][att]][0],"learnTable[ins][len(attOpenList)]",
            #      learnTable[ins][len(attOpenList)] )

            #print()
            infoArray[att][learnTable[ins][att]][0] += learnTable[ins][len(attOpenList)]# count "yes" to position[0]
            infoArray[att][learnTable[ins][att]][1] += abs((learnTable[ins][len(attOpenList)]-1)*-1)#"no" to position[1]
            infoArray[att][learnTable[ins][att]][2] += 1
        thisLearnTableCut += 1
    #print("thisLearnTableCut:", thisLearnTableCut)
    # ----------------------------------------------------------------------
    # 2. We run on "infoArray" (3D) and calculate "info" and "chiTest" for this threshold, for each possible attribute
    # as vertices. we take the best (with lowest info), but only if his "p-value" < "Alfa" (0.05),
    # if the chosen vertices for this threshold is not pass "chiTest", we prune this threshold as vertices
    for att in (attOpenList):
        thisAttributeInfo = 0
        for thresh in range(treshQty):
            if infoArray[att][thresh][2] > 0:
                if infoArray[att][thresh][0] > 0:
                     A1 = -(infoArray[att][thresh][0] / infoArray[att][thresh][2]) \
                         * math.log(infoArray[att][thresh][0] / infoArray[att][thresh][2], 10)
                if infoArray[att][thresh][1] > 0:
                     A2 = -(infoArray[att][thresh][1] / infoArray[att][thresh][2]) \
                         * math.log(infoArray[att][thresh][1] / infoArray[att][thresh][2], 10)
                infoArray[att][thresh][3] = A1 + A2
            thisAttributeInfo += infoArray[att][thresh][3] * (infoArray[att][thresh][2] / learnTableSize)
            # ----------------------------------------------------------------------------------------------
        # 4. Keep the best attribute
        if thisAttributeInfo < bestAtt[1]:
            bestAtt[0] = attOpenList[att]
            bestAtt[1] = thisAttributeInfo
            #print("new best att:", bestAtt[0], "info:", bestAtt[1])
    """
    print("infoArray for the best att (bestAtt(0)) after calculate Entropy ")
    print(bestAtt[0], "    Y    N   tot   E(Thre)  DsumY DsumN")
    print("--   ---  ---  ---   -------  ----- -----")
    tmp = attOpenList.index(bestAtt[0])
    for j in range(treshQty):
        print(j, '{:>5d}{:>5d}{:>5d}{:>10.5f}{:>7d}{:>6d}{:>8.1f}{:>8.1f}'
              .format(infoArray[tmp][j][0], infoArray[tmp][j][1], infoArray[tmp][j][2],
                      infoArray[tmp][j][3], infoArray[tmp][j][4], infoArray[tmp][j][5],
                      infoArray[tmp][j][6], infoArray[tmp][j][7]))
    print("--  ---  ---  ---   -------  ----  -----")
    """
    # ---------------------------------------------------------
    """
    # ---------------------------------------------------------

    for i in range(len(attOpenList)):
        print()
        print(attOpenList[i], "  Y    N   tot   E(Thre)  DsumY DsumN")
        print("--  ---  ---  ---   -------  ----- -----")
        tot = 0
        for j in range(treshQty):
            print(j, '{:>5d}{:>5d}{:>5d}{:>10.5f}{:>7d}{:>6d}{:>8.1f}{:>8.1f}'.format(infoArray[i][j][0],
                    infoArray[i][j][1], infoArray[i][j][2], infoArray[i][j][3], infoArray[i][j][4],
                    infoArray[i][j][5], infoArray[i][j][6], infoArray[i][j][7]))
            tot += infoArray[i][j][2]
        print("--  ---  ---  ---   -------  ----  -----")
        print("total:", tot)
    """
    #-----------------------------------------------------------------------------
    bestAtt[2] = infoArray[attOpenList.index(bestAtt[0])]
    #print("bestAtt[2]:", bestAtt[2])
    return bestAtt  # at [0] the attribute, at [1] its connections, at [2] infoArray for the best attribute

#=====================================================================================
def bestAttribute(learnTable, learnTableSize, learnTableSpamIndex, treshQty, attOpenList, attToCheck, threshToCheck):
    #----------------------------------------------------------------------------------------------
    # 1. run on "learn" table and creates 3D "infoArray" that accumulates Y/N spame to attributeQty X thresholdsQty X 5
    bestAtt = [666, 666, 666]
    thisLearnTableCut = 0
    history = []
    priviesNode = attToCheck
    while priviesNode != 'start': # create the privies connection, to split learnTable
        priviesThresh = dt[priviesNode][0][0]
        priviesNode = dt[priviesNode][0][1]
        if priviesNode != 'start':
            history.append([priviesNode, priviesThresh])
        #print("history", history)
    infoArray = [[[0 for k in range(8)] for j in range(treshQty)] for i in range(len(attOpenList))]#create "0" 3D array
    #----------- Run on LearnTable allocates lines with ----------------------
    for ins in range(learnTableSize): # learnTable[0] contains header 1..attQty, so we start from ins+1
        hits = 0
        for toIgnore in history:
            #print("toIgnor:", toIgnore, "ins:", ins, "ignor[0]:",toIgnore[0],"ignor[1]", toIgnore[1])
            if learnTable[ins][toIgnore[0]] == toIgnore[1]:
                hits += 1
        #print("ins:", ins, "hits:",hits,"toIgnore[0]",toIgnore[0],"toIgnore[1]",toIgnore[1])
        if learnTable[ins][attToCheck] == threshToCheck and hits == len(history):
            thisLearnTableCut += 1
            #--------- If the line in LearnTable meets criteria, update InfoArray ------------
            for openAtt in (attOpenList):
                x = attOpenList.index(openAtt) # infoArray is for open attributes only, we use index to know att# in coll
                #print("att:", openAtt,"x:",x)
                if openAtt != attToCheck and learnTable[ins][attToCheck] == threshToCheck:
                    # For each threshold, count "yes" and "no" to position[0] and [1]
                    infoArray[x][learnTable[ins][openAtt]][0]+=learnTable[ins][learnTableSpamIndex]
                    infoArray[x][learnTable[ins][openAtt]][1]+=abs((learnTable[ins][learnTableSpamIndex]-1)*-1)
                    infoArray[x][learnTable[ins][openAtt]][2]+=1
    #print("thisLearnTableCut:", thisLearnTableCut)
    #----------------------------------------------------------------------
    # 2. We run on "infoArray" (3D) and calculate "info" and "chiTest" for this threshold, for each possible attribute
    # as vertices. we take the best (with lowest info), but only if his "p-value" < "Alfa" (0.05),
    # if the chosen vertices for this threshold is not pass "chiTest", we prune this threshold as vertices
    for colNum in range(len(attOpenList)):
        thisAttributeInfo = 0
        for thresh in range(treshQty):
            A1 = A2 = 0
            #print("check infoArray with:", colNum, thresh)
            if infoArray[colNum][thresh][2] > 0:
                if infoArray[colNum][thresh][0] > 0:
                    A1 = -(infoArray[colNum][thresh][0] / infoArray[colNum][thresh][2]) \
                         * math.log(infoArray[colNum][thresh][0] / infoArray[colNum][thresh][2], 10)
                if infoArray[colNum][thresh][1] > 0:
                    A2 = -(infoArray[colNum][thresh][1] / infoArray[colNum][thresh][2]) \
                         * math.log(infoArray[colNum][thresh][1] / infoArray[colNum][thresh][2], 10)
                infoArray[colNum][thresh][3] = A1 + A2
            if thisLearnTableCut > 0:
                thisAttributeInfo += infoArray[colNum][thresh][3] * (infoArray[colNum][thresh][2] / thisLearnTableCut)
            # ----------------------------------------------------------------------------------------------
            # 4. Keep the best attribute
            if thisAttributeInfo < bestAtt[1]:
                bestAtt[0] = attOpenList[colNum]
                bestAtt[1] = thisAttributeInfo
                #print("new best att:", bestAtt[0], "info:", bestAtt[1])
    #-----------------------------------------------------------------------------------------------
    #print("freedom degree:", d-1, ", chiSquare:", '{:>4.1f}'.format(chiSquare), ", p-value:", '{:>15.15f}'.format(p_value))
    #---------------------------------------------------------
    """
    # ---------------------------------------------------------
    
    for i in range(len(attOpenList)):
        print()
        print(attOpenList[i], "  Y    N   tot   E(Thre)  DsumY DsumN")
        print("--  ---  ---  ---   -------  ----- -----")
        tot = 0
        for j in range(treshQty):
            print(j, '{:>5d}{:>5d}{:>5d}{:>10.5f}{:>7d}{:>6d}{:>8.1f}{:>8.1f}'.format(infoArray[i][j][0],
                    infoArray[i][j][1], infoArray[i][j][2], infoArray[i][j][3], infoArray[i][j][4],
                    infoArray[i][j][5], infoArray[i][j][6], infoArray[i][j][7]))
            tot += infoArray[i][j][2]
        print("--  ---  ---  ---   -------  ----  -----")
        print("total:", tot)
    """
    #-------------------------------------------------------
    #print("bestAtt[0]:", bestAtt[0])
    if bestAtt[0] < 666:
        bestAtt[2] = infoArray[attOpenList.index(bestAtt[0])]
    # print("bestAtt[2]:", bestAtt[2])
    else:
        bestAtt[2] = []
    return bestAtt  # at [0] the attribute, at [1] its connections, at [2] infoArray for the best attribute

#===========================================================
def chiTest (bestAttArray, treshQty):# in [0] thresh, in [1] accumulated data
    # 6. For the best attribute, calculate "chiTest" and "p-value" for prune decision
    chiSquare = 0
    thisBestThresh = 0
    toReturn = [0, 0, 0]
    thisBestThreshVerdict = 999
    d = 0
    for i in range(treshQty):
        # 3 Accumulate total Yes and total No for "chiTest" to coll [4] and [5]
        if i == 0:
            bestAttArray[i][4] = bestAttArray[i][0]
            bestAttArray[i][5] = bestAttArray[i][1]
        else:
            bestAttArray[i][4] = bestAttArray[i][0] + bestAttArray[i - 1][4]
            bestAttArray[i][5] = bestAttArray[i][1] + bestAttArray[i - 1][5]
        if bestAttArray[i][2] > 0:
            d += 1
    y = bestAttArray[treshQty - 1][4] + bestAttArray[treshQty - 1][5]  # total instances for this att and thresh
    for i in range(treshQty):
        if y > 0:
            bestAttArray[i][6] = bestAttArray[i][2] * bestAttArray[treshQty - 1][4] / y
            bestAttArray[i][7] = bestAttArray[i][2] * bestAttArray[treshQty - 1][5] / y
            #print("calculate chi to thresh:", i, "y:", y, "bestAttArray[i][6]:", bestAttArray[i][6],
            #      "bestAttArray[i][7]:", bestAttArray[i][7])
            if bestAttArray[i][6] != 0 and bestAttArray[i][7] != 0:
                chiSquare += ((bestAttArray[i][6] - bestAttArray[i][0]) ** 2 / bestAttArray[i][6] +
                        (bestAttArray[i][7] - bestAttArray[i][1]) ** 2 / bestAttArray[i][7])
            if bestAttArray[i][3] > thisBestThresh:
                thisBestThresh = bestAttArray[i][3]
                if bestAttArray[i][0] > bestAttArray[i][1]:
                    thisBestThreshVerdict = 888
                else:
                    thisBestThreshVerdict = 999
    pvalue = scipy.stats.chi2.pdf(chiSquare, d - 1)
    toReturn = [pvalue, thisBestThreshVerdict]
    """
    print("infoArray for the best att (bestAtt(0)) after calculate Entropy and chi")
    print("bestAtt[0]", "   Y    N   tot   E(Thre)  DsumY DsumN")
    print("--   ---  ---  ---   -------  ----- -----")
    for j in range(treshQty):
        print(j, '{:>5d}{:>5d}{:>5d}{:>10.5f}{:>7d}{:>6d}{:>8.1f}{:>8.1f}'
              .format(bestAttArray[j][0], bestAttArray[j][1], bestAttArray[j][2],
                      bestAttArray[j][3], bestAttArray[j][4], bestAttArray[j][5],
                      bestAttArray[j][6], bestAttArray[j][7]))
    print("--  ---  ---  ---   -------  ----  -----")
    """
    #print("freedom degree:", d - 1, ", chiSquare:", '{:>4.1f}'.format(chiSquare), ", p-value:",
    #      '{:>15.15f}'.format(pvalue))
    return toReturn

#====================================================
def findConnections(bestAttArray, treshQty):
    connections = []
    connectionsList = []
    defult = 999
    for i in range(treshQty):
        if bestAttArray[i][0] == 0 and bestAttArray[i][1] != 0:
            connections.append([i, 999])
        elif bestAttArray[i][1] == 0 and bestAttArray[i][0] != 0:
            connections.append([i, 888])
        elif bestAttArray[i][2] == 0:
            connections.append([i, defult])
        elif bestAttArray[i][2] != 0:
            connections.append([i, bestAttArray[i][3]])
    connections.sort(key=lambda x: x[1], reverse=False)
    for i in range(len(connections)):
        connectionsList.append(connections.pop(0))
    return connectionsList

#=====================================================
def addToTree(fatherAtt, conectedThresh, sunAtt):
    if fatherAtt not in dt.keys():
        dt[fatherAtt] = {}
        dt[fatherAtt][0] = []
        dt[fatherAtt][1] = {}
    if sunAtt not in dt.keys():
        dt[sunAtt] = {}
        dt[sunAtt][0] = []
        dt[sunAtt][1] = {}
    dt[fatherAtt][1][conectedThresh] = sunAtt
    dt[sunAtt][0] = [conectedThresh, fatherAtt]
#====================================================

def isThisSpam(mail):
    answer = dt['start'][1][0]
    #print("mail:", mail)
    #print("answer:", answer, "mail[answer]:", mail[answer], "dt.keys:", dt[answer][1].keys())
    while answer not in (888, 999):
        answer = dt[answer][1].get(mail[answer])
    if answer == 888:
        answer = 1
    else:
        answer = 0
    return answer
#=========================================

def printTree():
    print("                           connections to att via thresh (888-SPAM, 999-No SPAM)")
    print("                         ---------------------------------------------------------")
    print("Att   Under   Thresh      0     1     2     3     4     5     6     7     8     9 ")
    print("===   =====   ======     ===   ===   ===   ===   ===   ===   ===   ===   ===   ===")
    for i in dt.keys():
        if i not in ('start', 888, 999, 666, 777):
            print('{:>3}{:>8}{:>6}{:>11}{:>6}{:>6}{:>6}{:>6}{:>6}{:>6}{:>6}{:>6}{:>6}'
                  .format(i, dt[i][0][1], dt[i][0][0],
                          dt[i][1][0], dt[i][1][1], dt[i][1][2], dt[i][1][3],
                          dt[i][1][4], dt[i][1][5], dt[i][1][6],
                          dt[i][1][7], dt[i][1][8], dt[i][1][9]))
    print("===   =====   ======     ===   ===   ===   ===   ===   ===   ===   ===   ===   ===")

#=========================================
def buildTree(k):
    numOfTresholds = 10
    ratioOfLearFile = k*100 #%
    alfa = 0.05
    openNodesList = []
    learnAndTestTables = readFile('spambase.data', numOfTresholds, ratioOfLearFile)
    attOpenList = [i for i in range(learnAndTestTables[5])]
    rootAtt = root(learnAndTestTables[0], learnAndTestTables[1], numOfTresholds, attOpenList)  # find root
    addToTree('start', 0, rootAtt[0])
    attOpenList.remove(rootAtt[0])
    p_value = chiTest(rootAtt[2], numOfTresholds)
    if p_value[0] < alfa: # the best attribute pass chiSquare test
        toConnect = findConnections(rootAtt[2], numOfTresholds)
        #print("toConnect:", toConnect)
        for i in toConnect:
            if i[1] >= 100:
                addToTree(rootAtt[0], i[0], i[1])
            else:
                openNodesList.append([rootAtt[0], i[0]])
    else:
        dt[rootAtt[0]][1][rootAtt[1]] = p_value[1]
    #for i in dt.keys():
    #    print("dt[", i, "]", "=", dt[i])
    #print("on root picked attribute :", rootAtt[0], "connections", toConnect)
    #print("-----------------------------------------------")
    while len(openNodesList) > 0:
        #print("openNodesList:", openNodesList)
        nextNodeToAddToTree = openNodesList.pop(0)
        #print("go to bestAttribute with att:", nextNodeToAddToTree[0], "and thresh:", nextNodeToAddToTree[1])
        nextAtt = bestAttribute(learnAndTestTables[0], learnAndTestTables[1], learnAndTestTables[5],
                                numOfTresholds, attOpenList, nextNodeToAddToTree[0], nextNodeToAddToTree[1])
        if nextAtt[0] < 666:
            attOpenList.remove(nextAtt[0])
        #print("len(nextAtt[2])", len(nextAtt[2]))
        if len(nextAtt[2]) > 1:
            p_value = chiTest(nextAtt[2], numOfTresholds)
        if p_value[0] < alfa:  # the best attribute pass chiSquare test
            toConnect = findConnections(nextAtt[2], numOfTresholds)
            for i in toConnect:
                if i[1] > 100:
                    addToTree(nextAtt[0], i[0], i[1])
                else:
                    openNodesList.append([nextAtt[0], i[0]])
            addToTree(nextNodeToAddToTree[0], nextNodeToAddToTree[1], nextAtt[0])
        else:
            dt[nextNodeToAddToTree[0]][1][nextNodeToAddToTree[1]] = p_value[1]
    print("")
    printTree()

#=========================================
def buildTreeForK(learnArray):
    numOfTresholds = 10
    numOfAttributes = 57
    alfa = 0.05
    openNodesList = []
    attOpenList = [i for i in range(numOfAttributes)]
    rootAtt = root(learnArray, len(learnArray), numOfTresholds, attOpenList)  # find root
    addToTree('start', 0, rootAtt[0])
    attOpenList.remove(rootAtt[0])
    p_value = chiTest(rootAtt[2], numOfTresholds)
    if p_value[0] < alfa: # the best attribute pass chiSquare test
        toConnect = findConnections(rootAtt[2], numOfTresholds)
        #print("toConnect:", toConnect)
        for i in toConnect:
            if i[1] >= 100:
                addToTree(rootAtt[0], i[0], i[1])
            else:
                openNodesList.append([rootAtt[0], i[0]])
    else:
        dt[rootAtt[0]][1][rootAtt[1]] = p_value[1]
    #for i in dt.keys():
    #    print("dt[", i, "]", "=", dt[i])
    #print("on root picked attribute :", rootAtt[0], "connections", toConnect)
    #print("-----------------------------------------------")
    while len(openNodesList) > 0:
        #print("openNodesList:", openNodesList)
        nextNodeToAddToTree = openNodesList.pop(0)
        #print("go to bestAttribute with att:", nextNodeToAddToTree[0], "and thresh:", nextNodeToAddToTree[1])
        nextAtt = bestAttribute(learnTable, len(learnTable), numOfAttributes,
                                numOfTresholds, attOpenList, nextNodeToAddToTree[0], nextNodeToAddToTree[1])
        if nextAtt[0] < 666:
            attOpenList.remove(nextAtt[0])
        #print("len(nextAtt[2])", len(nextAtt[2]))
        if len(nextAtt[2]) > 1:
            p_value = chiTest(nextAtt[2], numOfTresholds)
        if p_value[0] < alfa:  # the best attribute pass chiSquare test
            toConnect = findConnections(nextAtt[2], numOfTresholds)
            for i in toConnect:
                if i[1] > 100:
                    addToTree(nextAtt[0], i[0], i[1])
                else:
                    openNodesList.append([nextAtt[0], i[0]])
            addToTree(nextNodeToAddToTree[0], nextNodeToAddToTree[1], nextAtt[0])
        else:
            dt[nextNodeToAddToTree[0]][1][nextNodeToAddToTree[1]] = p_value[1]
    #print("")
    #printTree()

#========================================================
def testTreeWithTestTable(testTable):
    results = {666: 0, 777: 0, 1: 0, 0: 0, 88: 0, 99: 0, 100: 0}
    for i in range(len(testTable)):
        if testTable[i][57] == 1:
            results[88] += 1
        else:
            results[99] += 1
        # print("theMail:", learnAndTestTables[2][i])
        yesOrNo = isThisSpam(testTable[i])
        results[yesOrNo] += 1
        if testTable[i][57] == 1 and yesOrNo == 1:
            results[100] += 1
        # print("yesOrNo:", yesOrNo)
    accuracy = int(results[100] / results[88] * 100)
    print("Test file size:", results[88] + results[99], "instances, ", results[88], "SPAM, and", results[99], "not")
    print("The Decision Tree marked", results[1], "as SPAM mails, and", results[0], "as Non SPAM")
    print("From the mails the DT classified as SPAM, only", results[100], "were actually SPAM, (",
          int(results[100] / results[1] * 100), "% )")
    print("From all the SPAM mails in the test file, the DT caught ", accuracy, "%")
    print("                    -----------------                           ")
    return accuracy
#=============================================================

def treeError(k):
    kDataArray = []
    t = 0
    for i in range(k):
        kDataArray.append([])
    # read the file into array, divided to thresholds
    readFileToThresholds('spambase.data', 10)
    for i in range(len(baseTable)):
        kBacket = random.randint(1, k)
        # split the big array into k random arrays
        kDataArray[kBacket-1].append(baseTable[i])
    # make the "k" small array to a test data, and combine all k-1 arrays to a learn data
    for i in range(k):
        testArray = []
        learnArray = []
        testArray = kDataArray[i]
        for j in range(k):
            if j != i:
                learnArray += kDataArray[j]
        # create a DT with the learn "k-1" data, test it on the "k" small array, and put results to "kResults"
        buildTreeForK(learnArray)
        t += testTreeWithTestTable(testArray)
    print()
    print("Tree error after k-cross validation:", int(t/k), "%")
    print("=============================================")


if __name__ == '__main__':
    print()
    print("            The Decision Tree after used 60% for learning")
    print("            =============================================")
    buildTree(0.6)
    print()
    print("The accuracy inspected in running the DT on the 40% test table")
    print("==============================================================")
    testTreeWithTestTable(testTable)
    print()
    print("Run K-cross validation")
    print("======================")
    treeError(10)


