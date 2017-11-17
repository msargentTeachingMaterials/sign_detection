def printConfusionMatrix(result, labels):
    result0 = [int(x) for x in result]

    falsePositives = 0
    falseNegatives = 0
    truePositives = 0
    trueNegatives = 0

    for i, row in enumerate(labels):
        if row  == 1 and result[i] == 1: 
            truePositives +=1
        if row  != 1 and result[i] != 1: 
            trueNegatives +=1
        if row  != 1 and result[i] == 1: 
            falsePositives +=1
        if row == 1 and result[i] != 1: 
            falseNegatives +=1	

    print "true pos:", truePositives, "true neg:", trueNegatives, "false pos:", falsePositives, "false neg:", falseNegatives, "\n"

