"""
    Module for generating attacker parameter
    Each entry in the file is a different type of attacker
        
    Asssumptions: For now we assume that attacker will have only searching sesssions
    So count for other session types will be only 1 & P will be 3600
"""
import string,datetime,time,pyparsing,argparse,os,sys,re,random,math
from argparse import ArgumentParser, ArgumentTypeError
from FcddosUtilities import getMinimumBotnetSize

def parseRange(string):
    tokens = string.split(',')
    rangeList = []
    if len(tokens) < 1:
        raise ArgumentTypeError("Invalid parameter range format")

    for token in tokens:
        rangeTokens = token.split(":")
        if not rangeTokens or len(rangeTokens) !=2:
            raise ArgumentTypeError("Invalid parameter range format")
        try:
            paramMinValue = int(rangeTokens[0].strip())
            paramMaxValue = int(rangeTokens[1].strip())
        except ValueError:
            try:
                paramMinValue = float(rangeTokens[0].strip())
                paramMaxValue = float(rangeTokens[1].strip())
            except ValueError:
                raise ArgumentTypeError("Invalid parameter range format")


        rangeList.append([paramMinValue,paramMaxValue])
    return rangeList

# parse commandline arguments
def parseCmdArgs():
    desc = "flash crowd attack generation tool"
    parametersRangesDesc = "attacker parameters ranges\n"+\
            "format: "+\
            "minValueParam1:maxValueParam1,"+\
            "minValueParam2:maxValueParam2,..."+\
            "minValueParamN:maxValueParamN \n"+\
            "Example: 1:10,11.0:201.0,11:220,1.0:10.0"
                            

    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-o", "--outfile", default=None,
            help="File to dump attackers parameters")
    parser.add_argument("-r", "--random-uniform", 
                        action='store_true', default=False,
            help="if given, attack parameter will be generated using "+\
                        "random uniform distribution")
    parser.add_argument("-n", "--num-attacker", type=int, required = True,
            help="Number of attacker to generate")
    parser.add_argument("-c", "--cutOff", type=int, required = True,
            help="attacker domain cutoff in terms of MB Size")
    parser.add_argument("-p", "--parametersRanges", type=parseRange,
            help=parametersRangesDesc)
    args = parser.parse_args()
    return args
def setAttackerAddress(attacker_address):
    if attacker_address[3] < 255:
        attacker_address[3]+=1
    elif attacker_address[2] < 255:
        attacker_address[2]+=1
        attacker_address[3]=0
    elif attacker_address[1] < 255:
        attacker_address[1]+=1
        attacker_address[2]=0
        attacker_address[3]=0
    else:
        attacker_address[0]+=1
        attacker_address[1]=0
        attacker_address[2]=0
        attacker_address[3]=0
    return attacker_address

def getNPraForOthers(N,P,r,a):
    browsingSes= []
    relaxedSes = []
    longSes = []
    """
    since attacker consist of only searching session, so
    N_other =1 for other session types
    P_other = 3600 for other session types
    """
    N_other =1
    P_other = 3600
    R = int(N * r) 
    r_other = R/N_other
    a_other = float(N*(r-1)*a +(N-1)*P)/(N*(r-1)+(N-1))
    """
    Don't add R in the parameter list so that it won't be used in trainig
    return [N_other,P_other,r_other,a_other,N_other,P_other,r_other,a_other,\
                N_other,P_other,r_other,a_other,R]
    """
    return [N_other,P_other,r_other,a_other,N_other,P_other,r_other,a_other,\
                N_other,P_other,r_other,a_other]

def randomUniformAttackerGenerate(args,outputStream,totalNumberOfAttackers):
    #M range
    min_session=int(args.num_session_range[0])
    max_session=int(args.num_session_range[1])
    #F range
    min_pause=float(args.pause_range[0])
    max_pause=float(args.pause_range[1])
    #T range
    min_req =float(args.num_request_range[0])
    max_req =float(args.num_request_range[1])
    i = 0
    attackerAddress = [256,0,0,0]
    while i < totalNumberOfAttackers:
        N = int(random.uniform(min_session,max_session))
        P = random.uniform(min_pause,max_pause)
        r = random.uniform(min_req,max_req)

        searchingSession = [N,P,r]
        parameters = searchingSession
        
        #write the parameters
        # convert list to comma seperated string
        # outputString = ",".join([str(round(x,2)) for x in parameters])
        outputString = str(parameters[0])+","+\
                str(round(parameters[1],2))+","+\
                str(parameters[2])
        outputString = '"'+".".join([str(x) for x in attackerAddress])+".0"'"'+\
                ","+outputString+",ATTACKER\n" 
        outputStream.write(outputString)
        attackerAddress = setAttackerAddress(attackerAddress)
        i+=1

attackerAddress = [256,0,0,0]
curAttId = 0
def fixedUniformAttackerGenerate(args,outputStream,totalNumberOfAttackers,
        MBCutOff):
    class Parameter:
        def __init__(self,parameterType,count,minValue,maxValue):
            self.parameterType = parameterType
            self.count = count
            self.minValue = minValue
            self.maxValue = maxValue
            self.distribution = None
        def setFixedUniformDistribution(self):
            if self.parameterType == int:
                self.distribution =[
                    int(round(
                        self.minValue+(
                            float(self.maxValue-self.minValue
                                       )
                            /self.count)*x
                    )) 
                    for x in range(self.count-1)]
                self.distribution.append(self.maxValue)
            elif self.parameterType == float:
                self.distribution =[
                    self.minValue+round(((float(
                        self.maxValue-self.minValue
                                       )
                        /self.count)*x),2)
                    for x in range(self.count-1)]
                #inset f =0 
                self.distribution.append(self.maxValue)
            else:
                print "Invalid Type specified: ",self.parameterType
                exit(0)
        def getFixedUniformDistribution(self):
            if self.distribution ==  None:
                self.setFixedUniformDistribution()
            return self.distribution
    
    def writeParametersToFile(outputStream,attackerParam,parameterObjects,
                              numberOfAttackers,MBCutOff):
        global attackerAddress
        global curAttId
        index = len(attackerParam)
        attackerParam.append(None)
        for parameter in parameterObjects[0].getFixedUniformDistribution():
            #terminate after going through all valid combinations
            """
            if curAttId >= numberOfAttackers:
                return
            """
            attackerParam[index] = parameter
            if len(parameterObjects) == 1:
                totalLevels = (len(attackerParam)-2)/2
                invalidAttackerParam = False
                prevLevelNValue = attackerParam[0]
                prevLevelPValue = attackerParam[1]
                for curIndex in range(totalLevels-1):
                    curLevelNValue = attackerParam[4+curIndex*2]
                    curLevelPValue = attackerParam[5+curIndex*2]
                    if curLevelNValue > prevLevelNValue:
                        invalidAttackerParam = True
                        break
                    elif curLevelPValue < prevLevelPValue:
                        invalidAttackerParam = True
                        break
                    prevLevelNValue = curLevelNValue
                    prevLevelPValue = curLevelPValue
                if invalidAttackerParam:
                    continue
                """
                if int(getMinimumBotnetSize(attackerParam)) > MBCutOff:
                    continue
                """
                #print " "*len(attackerParam),attackerParam 
                #write the parameters
                # convert list to comma seperated string
                outputString = ""
                for param in attackerParam:
                    if isinstance(param,int):
                        outputString += str(param)+","
                    elif isinstance(param,float):
                        outputString += str(round(param,2))+","
                    else:
                        print "invalid type of parameter", param
                        exit(0)
                outputString = '"'+\
                        ".".join([str(x) for x in attackerAddress])+\
                        ".0"'"'+\
                        ","+outputString+",ATTACKER\n" 
                outputStream.write(outputString)
                attackerAddress = setAttackerAddress(attackerAddress)
                curAttId+=1

            else:
                writeParametersToFile(outputStream,list(attackerParam),
                                      parameterObjects[1:],numberOfAttackers,
                                      MBCutOff)

    #num session range
    parameterValuesCount = int(math.ceil(totalNumberOfAttackers**(
        1.0/len(args.parametersRanges))))
    allParameters = []
    for parameterRange in args.parametersRanges:
        minValue = parameterRange[0]
        maxValue = parameterRange[1]
        if isinstance(minValue,float): 
            parameter = Parameter(float,parameterValuesCount,minValue,maxValue)
        else:
            parameter = Parameter(int,parameterValuesCount,minValue,maxValue)
        allParameters.append(parameter)
    writeParametersToFile(outputStream,[],allParameters,
                          totalNumberOfAttackers,MBCutOff)
if __name__ == "__main__":
    #parse commandlist arguments    
    args = parseCmdArgs()
    outputStream = None
    try:
        outputStream = open(args.outfile,"w")
    except:
        # happend when the outfile is specified incorrectly 
        # or not specified at all
        outputStream = sys.stdout
    totalNumberOfAttackers = args.num_attacker
    #totalNumberOfAttackers = 50
    if args.random_uniform:
        randomUniformAttackerGenerate(args,outputStream,totalNumberOfAttackers)
    else:
        fixedUniformAttackerGenerate(args,outputStream,totalNumberOfAttackers,
                args.cutOff)

    
