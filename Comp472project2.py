# March 29 2020
# Concordia University
# COMP 472 Section NN
# Project 2
# By:
# Jason Brennan - 27793928
# Maryam Eskandari - 40065716
# Martin Grezak - 25693810

import sys
import numpy as np
from operator import itemgetter, attrgetter
from enum import Enum
import time
import collections

# An enum class for flagging the language in use
class Language(Enum):
    EU = 0, 'Basque'
    CA = 1, 'Catalan'
    GL = 2, 'Galician'
    ES = 3, 'Spanish'
    EN = 4, 'English'
    PT = 5, 'Portugese'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value
class NestedDict: 
      
        def __init__(self): 
            self.head = collections.defaultdict(dict)
            self.originalCorpusSize=0
            self.VocabularySize = 26
            self.maxNestedGrade = 2
            self.smoothValue=0.5
    
        def __init__(self , ngram , vocabularySize , smoothValue): 
            self.head = collections.defaultdict(dict)
            self.originalCorpusSize=0
            self.VocabularySize = vocabularySize
            self.maxNestedGrade = ngram
            self.smoothValue=smoothValue
       
        def insertToken(self,Token): 
          
            #check Validation of Token
            if(len(Token)==self.maxNestedGrade):
                self.originalCorpusSize+=1
                currentDict=self.head
                for i in range (self.maxNestedGrade-1):
                    if(Token[i] not in currentDict):
                       currentDict[Token[i]]= collections.defaultdict(dict)
                    currentDict=currentDict[Token[i]]
                if(Token[self.maxNestedGrade-1] not in currentDict):
                       currentDict[Token[self.maxNestedGrade-1]]= 1
                else:
                    currentDict[Token[self.maxNestedGrade-1]]+= 1
            else:
                print("token is not valid!!")


        def getProbabilityGivenToken(self, Token): 
           # NLP slide 50&51 : p(w1w2w3)=(C(w1w2w3)+smooth)/(N+SMOOTH*B)
           probabilityDenominator=self.originalCorpusSize + ((self.VocabularySize**self.maxNestedGrade)*self.smoothValue)
           probability= 0
           if(len(Token)==self.maxNestedGrade):
                currentDict=self.head
                for i in range (self.maxNestedGrade-1):
                    if(Token[i] in currentDict):
                       currentDict=currentDict[Token[i]]
                    else:
                        return  self.smoothValue/probabilityDenominator
                if(Token[self.maxNestedGrade-1] in currentDict) :     
                    value =currentDict[Token[self.maxNestedGrade-1]]
                    probability = (value+self.smoothValue)/probabilityDenominator
                else :
                    probability = self.smoothValue/probabilityDenominator
            
            
           else:
                print("token is not valid!!")
       
           return probability
  
class NgramDict: 
      
        def __init__(self): 
            self.ngramTable = collections.defaultdict(dict)
            self.originalCorpusSize=0
            self.VocabularySize = 26
            self.tokenSize = 2
            self.smoothValue=0.5
    
        def __init__(self , ngram , vocabularySize , smoothValue): 
            self.ngramTable = collections.defaultdict(dict)
            self.originalCorpusSize=0
            self.VocabularySize = vocabularySize
            self.tokenSize = ngram
            self.smoothValue=smoothValue
       
        def insertToken(self,Token): 
          
            #check Validation of Token
            if(len(Token)==self.tokenSize):
                self.originalCorpusSize+=1
                
                if(Token not in self.ngramTable):
                       self.ngramTable[Token]= 1
                else:
                    self.ngramTable[Token]+= 1
            else:
                print("token is not valid!!")

        def evaluateSmoothValue(self):
            #evaluate smooth value such that the fake corpus size will be proportional to original corpus size
            self.smoothValue= self.originalCorpusSize/(self.VocabularySize**self.tokenSize)
        
        def getProbabilityGivenToken(self, Token): 
           # NLP slide 50&51 : p(w1w2w3)=(C(w1w2w3)+smooth)/(N+SMOOTH*B)
           probabilityDenominator=self.originalCorpusSize + ((self.VocabularySize**self.tokenSize)*self.smoothValue)
           probability= 0
           if(len(Token)==self.tokenSize):
                if(Token in self.ngramTable) :     
                    value =self.ngramTable[Token]
                    probability = (value+self.smoothValue)/probabilityDenominator
                else :
                    probability = self.smoothValue/probabilityDenominator
                    
           else:
                print("token is not valid!!")
       
           return probability
  
class LangModel:
    indexByVocabulary_1_dict ={}
    indexByVocabulary_2_dict ={}
    indexByVocabulary_3_dict ={}

    # default constructor
    def __init__(self):
        self.vocabulary = self.getVocabulary()
        self.ngram = self.getNgram()
        self.smoothing = self.getSmoothing()
        self.trainingFile = self.getTrainingFile()
        self.testingFile = self.getTestFile()

        # each language models below will receive a Matrix generated by the vocabulary and n-gram parameters
        #self.EU = self.generateMatrix(self.ngram, self.vocabulary)
        #self.CA = self.generateMatrix(self.ngram, self.vocabulary)
        #self.GL = self.generateMatrix(self.ngram, self.vocabulary)
        #self.ES = self.generateMatrix(self.ngram, self.vocabulary)
        #self.EN = self.generateMatrix(self.ngram, self.vocabulary)
        #self.PT = self.generateMatrix(self.ngram, self.vocabulary)


    #parameterized constructor
    def __init__(self,vocabulary=-1,ngram=-1,smoothing=0,trainingFile="",testingFile=""):
        self.generateIndexByVocabulary()
        self.vocabularyType = vocabulary
        self.vocabulary = self.getVocabulary(vocabulary)
        self.ngram = self.getNgram(ngram)
        self.smoothing = self.getSmoothing(smoothing)
        self.trainingFile = self.getTrainingFile("training-tweets.txt")
        #self.trainingFile = self.getTrainingFile(trainingFile)

        #self.testingFile = self.getTestFile("training-tweets.txt")
        self.testingFile = self.getTestFile("test-tweets-given.txt")
        #self.testingFile = self.getTestFile(testingFile)

         # each language models below will receive a Matrix generated by the vocabulary and n-gram parameters
        self.EU = NgramDict(self.ngram, len(self.vocabulary) , self.smoothing)
        self.CA = NgramDict(self.ngram, len(self.vocabulary) , self.smoothing)
        self.GL = NgramDict(self.ngram, len(self.vocabulary) , self.smoothing)
        self.ES = NgramDict(self.ngram, len(self.vocabulary) , self.smoothing)
        self.EN = NgramDict(self.ngram, len(self.vocabulary) , self.smoothing)
        self.PT = NgramDict(self.ngram, len(self.vocabulary) , self.smoothing)

        self.languageProbability = {
            Language.EU: 0.0,
            Language.CA: 0.0,
            Language.GL: 0.0,
            Language.ES: 0.0,
            Language.EN: 0.0,
            Language.PT: 0.0
        }

        # test--------------------------
        #self.increaseSeenEventGivenToken_NestedDict("abc" , 0)
        #self.increaseSeenEventGivenToken_NestedDict("abc" , 0)
        #self.increaseSeenEventGivenToken_NestedDict("abc" , 0)
        #self.increaseSeenEventGivenToken_NestedDict("abc" , 0)
        #self.increaseSeenEventGivenToken_NestedDict("abc" , 0)
        #self.increaseSeenEventGivenToken_NestedDict("abc" , 0)
        
        #print (self.getProbabilityGivenToken_NestedDict("abc" , 0))
        #print (self.getProbabilityGivenToken_NestedDict("acc" , 0))
        #---------------------------------

    def getVocabulary(self,vocabulary=-1):

        choice = vocabulary

        if(choice==-1):
            print("Select a number for which vocabulary you would like to use:")
            print("0 : Fold the corpus to lowercase and use only the 26 letters of the alphabet [a-z]")
            print("1 : Distinguish up and low cases and use only the 26 letters of the alphabet [a-z,A-Z]")
            print("2 : Distinguish up and low cases and use all characters accepted by the built-in isalpha() method")
            choice = int(input ("Enter your choice: "))

        switcher = {
            0: self.generateVocabulary(0),
            1: self.generateVocabulary(1),
            2: self.generateVocabulary(2)
            }
        
        return switcher.get(choice,"Invalid selection")

    def getNgram(self,ngram=-1):

        choice = ngram

        if(choice==-1):
            print("Select a number for which size n-gram you would like to use:")
            print("1 : character unigrams")
            print("2 : character bigrams")
            print("3 : character trigrams")
            choice = int(input ("Enter your choice: "))

        switcher = {
            1: 1,
            2: 2,
            3: 3
            }
        
        return switcher.get(choice,"Invalid selection")

    def getSmoothing(self,smoothing=0):

        choice = smoothing

        if(choice==0):

            interrupt = False
            count = 0
                
            while(not interrupt):
                    
                count = count + 1
                    
                choice = float(input ("Enter a smoothing value between 0 and 1 : "))
                    
                if(choice>=0 or choice<=1):
                    interrupt = True
                    
                if(count>3):
                    print("You failed to provide a smoothing value between 0 and 1, program will continue with default value: 0 ")
                    choice==0
                    interrupt = True
        
        return choice

    def getTrainingFile(self,trainingFile=""):

        dataSet = list()
        fileName = trainingFile
        count = 0

        try:
            # read the data into a list
            with open(str(fileName), encoding='utf-8-sig') as file:
                dataSet = file.readlines()

        except FileNotFoundError :
            print("File does not exist")
            fileName=""

        if(fileName==""):

            interrupt = False
            count = 0
            while(not interrupt):
                count = count + 1
                fileName = input ("Enter a valid TRAINING file name with the extension : ")
                
                try:
                    # read the data into a list
                    with open(str(fileName), encoding='utf-8-sig') as file:
                        dataSet = file.readlines()

                except FileNotFoundError :
                    print("File does not exist")

                
                if(len(dataSet)>0):
                    interrupt = True
                    
                if(count>3):
                    print("You failed to provide a valid TRAINING file, program will use default training dataset")
                    
                    fileName = "training-tweets.txt"

                    # read the data into a list
                    with open(str(fileName), encoding='utf-8-sig') as file:
                        dataSet = file.readlines()

                    interrupt = True

        return dataSet


    def getTestFile(self,testFile=""):

        dataSet = list()
        fileName = testFile
        count = 0

        try:
            # read the data into a list
            with open(str(fileName), encoding='utf-8-sig') as file:
                dataSet = file.readlines()

        except FileNotFoundError :
            print("File does not exist")
            fileName=""

        if(fileName==""):

            interrupt = False
            count = 0

            while(not interrupt):
                count = count + 1
                fileName = input ("Enter a valid TEST file name with the extension : ")
                
                try:
                    # read the data into a list
                    with open(str(fileName), encoding='utf-8-sig') as file:
                        dataSet = file.readlines()

                except FileNotFoundError :
                    print("File does not exist")

                
                if(len(dataSet)>0):
                    interrupt = True
                    
                if(count>3):
                    print("You failed to provide a valid TEST file, program will use default training dataset")
                    
                    fileName = "test-tweets-given.txt"

                        # read the data into a list
                    with open(str(fileName), encoding='utf-8-sig') as file:
                        dataSet = file.readlines()

                    interrupt = True

        return dataSet

    def generateVocabulary(self, selection):

        select = selection

        if(select==0):

            dataSet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x','y','z']
        
        elif (select==1):

            dataSet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

        elif(select==2):
            
            fileName = "utf8.txt"
            dataSet = list()

            # read the data into a list
            with open(str(fileName), encoding="utf8") as file:

              while True:
                char = file.read(1)
                if not char:
                  break
                if(char.isalpha() and char!=" "):
                    dataSet.append(char)
            
            #remove duplicates from the dataSet
            if len(dataSet) != len(set(dataSet)):
                dataSet = list(set(dataSet))
  
        return dataSet

    def generateMatrix(self,ngram,vocabulary , smoothingVal):

        size = len(vocabulary)
        ngramMatrix = np.zeros

        if(ngram==1):
            ngramMatrix = np.full(size + 1, smoothingVal)
            ngramMatrix[-1] = size * smoothingVal
           
        elif(ngram==2):
            ngramMatrix = np.full((size,size+1), smoothingVal, dtype=np.half)
            for row in ngramMatrix:
                row[-1] = size * smoothingVal
        
        elif(ngram==3):
            ngramMatrix = np.full((size,size,size+1), smoothingVal , dtype=np.half)
            for row in ngramMatrix:
                for depth in row:
                    depth[-1] = size * smoothingVal

        return ngramMatrix
         
    def increaseSeenEventGivenToken_MatrixModel(self , token , language):
         
        switcherVocabularyType = {
            0: LangModel.indexByVocabulary_1_dict,
            1: LangModel.indexByVocabulary_2_dict,
            2: LangModel.indexByVocabulary_3_dict
            }
         
        switcherLanguage = {
             0: self.EU,
             1: self.CA,
             2: self.GL,
             3: self.ES,
             4: self.EN,
             5: self.PT
            }
       
        
        if self.ngram ==1 :
            table = switcherLanguage.get(language)
            table[switcherVocabularyType.get(self.vocabularyType)[token]]+=1
            table[-1] += 1
        
        elif self.ngram==2:
            table = switcherLanguage.get(language)
            row = table[switcherVocabularyType.get(self.vocabularyType)[token[0]]]
            row[switcherVocabularyType.get(self.vocabularyType)[token[1]]]+=1
            row[-1] += 1

        else:
            table = switcherLanguage.get(language)
            row = table[switcherVocabularyType.get(self.vocabularyType)[token[0]]]
            depth = row[switcherVocabularyType.get(self.vocabularyType)[token[1]]]
            depth[switcherVocabularyType.get(self.vocabularyType)[token[2]]]+=1
            depth[-1] += 1
        
    def getProbabilityGivenToken_MatrixModel(self , token , language):
         
        switcherVocabularyType = {
            0: LangModel.indexByVocabulary_1_dict,
            1: LangModel.indexByVocabulary_2_dict,
            2: LangModel.indexByVocabulary_3_dict
            }
         
        switcherLanguage = {
             0: self.EU,
             1: self.CA,
             2: self.GL,
             3: self.ES,
             4: self.EN,
             5: self.PT
            }
        
        if self.ngram ==1 :
            table = switcherLanguage.get(language)
            return table[switcherVocabularyType.get(self.vocabularyType)[token]] / table[-1]
        elif self.ngram==2:
            table = switcherLanguage.get(language)
            row = table[switcherVocabularyType.get(self.vocabularyType)[token[0]]]
            return row[switcherVocabularyType.get(self.vocabularyType)[token[1]]] / row[-1]
            #return(switcherLanguage.get(language)[switcherVocabularyType.get(self.vocabularyType)[token[0]]][switcherVocabularyType.get(self.vocabularyType)[token[1]]])
        else:
            table = switcherLanguage.get(language)
            row = table[switcherVocabularyType.get(self.vocabularyType)[token[0]]]
            depth = row[switcherVocabularyType.get(self.vocabularyType)[token[1]]]
            return depth[switcherVocabularyType.get(self.vocabularyType)[token[2]]] / depth[-1]
            #return(switcherLanguage.get(language)[switcherVocabularyType.get(self.vocabularyType)[token[0]]][switcherVocabularyType.get(self.vocabularyType)[token[1]]][switcherVocabularyType.get(self.vocabularyType)[token[2]]]) 
  
    def increaseSeenEventGivenToken_NestedDict(self , token , language):
               
        switcherLanguage = {
             0: self.EU,
             1: self.CA,
             2: self.GL,
             3: self.ES,
             4: self.EN,
             5: self.PT
            }
       
        table = switcherLanguage.get(language)
        table.insertToken(token)
        
        
    def getProbabilityGivenToken_NestedDict(self , token , language):
         
                
        switcherLanguage = {
             0: self.EU,
             1: self.CA,
             2: self.GL,
             3: self.ES,
             4: self.EN,
             5: self.PT
            }
        table = switcherLanguage.get(language)
        return table.getProbabilityGivenToken(token)
        
    def generateIndexByVocabulary(self):
        for i in range(3):
            vocabulary = self.generateVocabulary(i)
            size = len(vocabulary)
            indexDict = {}
            index = 0
            for j in range (size ):
                 indexDict[vocabulary[j]] = index
                 index+=1
            if i == 0 :
                LangModel.indexByVocabulary_1_dict =indexDict
            
            elif i==1:
                LangModel.indexByVocabulary_2_dict=indexDict
            else:
                
                LangModel.indexByVocabulary_3_dict=indexDict

    def generateDict_m(self,ngram,vocabulary , smoothingVal):

        size = len(vocabulary)
        ngramDict = {}
    
        return ngramDict

    def generateProbabilityTable(self):
        # split the training file by tabs
        self.splitTrainingFile()

        # read trainingFile[i][-1] character by character, convert to lower case if using vocabulary 0
        countOfTweets = 0
        if self.vocabularyType == 0:
            for line in self.trainingFile:
                countOfTweets += 1
                language = self.stringToLanguageEnum(line[2])

                # increment the occurences of this particular language, and the occurences of the ngrams
                self.languageProbability[language] += 1
                self.parseNgrams(language, line[-1].lower())
        else:
            for line in self.trainingFile:
                countOfTweets += 1
                language = self.stringToLanguageEnum(line[2])

                # increment the occurences of this particular language, and the occurences of the ngrams
                self.languageProbability[language] += 1
                self.parseNgrams(language, line[-1])

        # calculate P(language) by divind occurences by the total number of tweets
        for k in self.languageProbability.keys():
            self.languageProbability[k] /= countOfTweets

    def splitTrainingFile(self):
        for i in range(len(self.trainingFile)):
            # split the lines in the training file by the first 3 tabs
            self.trainingFile[i] = self.trainingFile[i].split("\t", 3)

            # remove trailing newline character at the end of the tweet
            self.trainingFile[i][-1] = self.trainingFile[i][-1][0:len(self.trainingFile[i][-1])-1]

    def stringToLanguageEnum(self, str):
        if str == "eu":
            return Language.EU
        elif str == "ca":
            return Language.CA
        elif str == "gl":
            return Language.GL
        elif str == "es":
            return Language.ES
        elif str == "en":
            return Language.EN
        elif str == "pt":
            return Language.PT
        else:
            return None

    def LanguageEnumToString(self, language):
        if language == Language.EU:
            return "eu"
        elif language == Language.CA:
            return "ca"
        elif language == Language.GL:
            return "gl"
        elif language == Language.ES:
            return "es"
        elif language == Language.EN:
            return "en"
        elif language == Language.PT:
            return "pt"
        else:
            return None

    def existsInVocab(self, str):
        for character in str:
            if character not in self.vocabulary:
                return False
        return True

    def parseNgrams(self, language, str):
        for i in range(len(str) - self.ngram):
            substr = str[i:(i + self.ngram)]
            if self.existsInVocab(substr):
                self.increaseSeenEventGivenToken_NestedDict(substr, int(language))
                #self.increaseSeenEventGivenToken_MatrixModel(substr, int(language))

    def processTweet(self, line):
        # split the line in the training file by tabs
        line = line.split("\t", 3)
        # remove trailing newline character
        line[-1] = line[-1][0:len(line[-1]) - 1]

        # dictionary to store scores
        score = {
            Language.EU: 0.0,
            Language.CA: 0.0,
            Language.GL: 0.0,
            Language.ES: 0.0,
            Language.EN: 0.0,
            Language.PT: 0.0
        }

        # token = "aabbc"
        # P(EU) + P(a|a) + P(b|a) + P(b|b) + P(c|b)
        #correct Formula:
        #score(EU)= P(EU) + P(aa|EU) + P(ab|EU) + P(bb|EU) + P(bc|EU)
        for i in range(len(line[-1]) - self.ngram):
            substr = line[-1][i:(i + self.ngram)]
            if self.existsInVocab(substr):
                for k in score.keys():
                    score[k] += np.log10(self.getProbabilityGivenToken_NestedDict(substr, int(k)))
                    #score[k] += np.log10(self.getProbabilityGivenToken_MatrixModel(substr, int(k)))

        highestPair = [None, float("-inf")]
        for k in score.keys():
            score[k] += np.log10(self.languageProbability[k])
            if score[k] > highestPair[1]:
                highestPair[0] = k
                highestPair[1] = score[k]
             
        result = list()
        result.append(line[0])
        result.append(self.LanguageEnumToString(highestPair[0]))
        result.append(highestPair[1])
        result.append(line[2])
        result.append("correct" if result[1] == result[3] else "wrong")

        return result
            
    def printResults(self,byomFlag=0):

        #----------------Trace File Section-----------------------------
        
        #Metrics for Accuracy
        countWrong = 0
        countCorrect = 0

        #Metrics for True Positive
        metricsDict = {'eu':{'truePositive':0, 'falsePositive':0,'falseNegative':0, 'modelCount':0},
                       'ca':{'truePositive':0, 'falsePositive':0,'falseNegative':0, 'modelCount':0},
                       'gl':{'truePositive':0, 'falsePositive':0,'falseNegative':0, 'modelCount':0},
                       'es':{'truePositive':0, 'falsePositive':0,'falseNegative':0, 'modelCount':0},
                       'en':{'truePositive':0, 'falsePositive':0,'falseNegative':0, 'modelCount':0},
                       'pt':{'truePositive':0, 'falsePositive':0,'falseNegative':0, 'modelCount':0}}
               
        #Compose file name
        traceFileName = "trace_" + str(len(self.vocabulary)) +"_"+ str(self.ngram) +"_"+ str(self.smoothing) +".txt"
        
        #Hard code file name for Build Your Own Model
        if byomFlag == 1:
            traceFileName = "trace_myModel.txt"
            
        #Open file
        file = open(traceFileName, 'w')

        for i in range(len(self.testingFile)):
            result = self.processTweet(self.testingFile[i])
       
            #Map out each entry passed
            tweetID = str(result[0])
            mostLikelyClass = str(result[1])
            mostLikelyScore = str(result[2])
            correctClass = str(result[3])
            outcome = str(result[4]) 

            traceOutputString = tweetID + "  " + mostLikelyClass + "  " + mostLikelyScore + "  " + correctClass + "  " + outcome + "\n"
            file.write(traceOutputString)

            #Increase the counter of the model by 1
            metricsDict[correctClass]['modelCount'] = metricsDict[correctClass]['modelCount'] + 1

            if outcome=="correct":
                
                #Increase the Correct counter by 1
                countCorrect = countCorrect + 1
            
                #+1 the model of the correctClass/mostLikelyClass as they are one and the same
                metricsDict[correctClass]['truePositive'] = metricsDict[correctClass]['truePositive'] + 1

             
            else:
                
                #Increase the Wrong counter by 1
                countWrong = countWrong + 1

                #+1 the model of the correctClass for not recognizing a tweet in its language
                metricsDict[correctClass]['falseNegative'] = metricsDict[correctClass]['falseNegative'] + 1

                #+1 the model of the mostLikelyClass for thinking tweet belongs to its language
                metricsDict[mostLikelyClass]['falsePositive'] = metricsDict[mostLikelyClass]['falsePositive'] + 1


        #Finally
        file.close()

        #----------------Overall Evaluation File Section ---------------

        #Metrics for Precision
        #eu_P = ca_P = gl_P = es_P = en_P = pt_P = 0.00

        numerator = float(metricsDict['eu']['truePositive'])
        if numerator == 0:
            eu_P = 0.0
        else:
            eu_P = numerator / (numerator + float(metricsDict['eu']['falsePositive']))

        numerator = float(metricsDict['ca']['truePositive'])
        if numerator == 0:
            ca_P = 0.0
        else:
            ca_P = numerator / (numerator + float(metricsDict['ca']['falsePositive']))

        numerator = float(metricsDict['gl']['truePositive'])
        if numerator == 0:
            gl_P = 0.0
        else:
            gl_P = numerator / (numerator + float(metricsDict['gl']['falsePositive']))

        numerator = float(metricsDict['es']['truePositive'])
        if numerator == 0:
            es_P = 0.0
        else:
            es_P = numerator / (numerator + float(metricsDict['es']['falsePositive']))

        numerator = float(metricsDict['en']['truePositive'])
        if numerator == 0:
            en_P = 0.0
        else:
            en_P = numerator / (numerator + float(metricsDict['en']['falsePositive']))

        numerator = float(metricsDict['pt']['truePositive'])
        if numerator == 0:
            pt_P = 0.0
        else:
            pt_P = numerator / (numerator + float(metricsDict['pt']['falsePositive']))

        #eu_P = float(metricsDict['eu']['truePositive']) / (float(metricsDict['eu']['truePositive'])+float(metricsDict['eu']['falsePositive']))
        #ca_P = float(metricsDict['ca']['truePositive']) / (float(metricsDict['ca']['truePositive'])+float(metricsDict['ca']['falsePositive']))
        #gl_P = float(metricsDict['gl']['truePositive']) / (float(metricsDict['gl']['truePositive'])+float(metricsDict['gl']['falsePositive']))
        #es_P = float(metricsDict['es']['truePositive']) / (float(metricsDict['es']['truePositive'])+float(metricsDict['es']['falsePositive']))
        #en_P = float(metricsDict['en']['truePositive']) / (float(metricsDict['en']['truePositive'])+float(metricsDict['en']['falsePositive']))
        #pt_P = float(metricsDict['pt']['truePositive']) / (float(metricsDict['pt']['truePositive'])+float(metricsDict['pt']['falsePositive']))

        #Metrics for Recall
        #eu_R = ca_R = gl_R = es_R = en_R = pt_R = 0.00

        numerator = float(metricsDict['eu']['truePositive'])
        if numerator == 0:
            eu_R = 0.0
        else:
            eu_R = numerator / (numerator + float(metricsDict['eu']['falseNegative']))

        numerator = float(metricsDict['ca']['truePositive'])
        if numerator == 0:
            ca_R = 0.0
        else:
            ca_R = numerator / (numerator + float(metricsDict['ca']['falseNegative']))

        numerator = float(metricsDict['gl']['truePositive'])
        if numerator == 0:
            gl_R = 0.0
        else:
            gl_R = numerator / (numerator + float(metricsDict['gl']['falseNegative']))

        numerator = float(metricsDict['es']['truePositive'])
        if numerator == 0:
            es_R = 0.0
        else:
            es_R = numerator / (numerator + float(metricsDict['es']['falseNegative']))

        numerator = float(metricsDict['en']['truePositive'])
        if numerator == 0:
            en_R = 0.0
        else:
            en_R = numerator / (numerator + float(metricsDict['en']['falseNegative']))

        numerator = float(metricsDict['pt']['truePositive'])
        if numerator == 0:
            pt_R = 0.0
        else:
            pt_R = numerator / (numerator + float(metricsDict['pt']['falseNegative']))

        #eu_R = float(metricsDict['eu']['truePositive'])/(float(metricsDict['eu']['truePositive'])+float(float(metricsDict['eu']['falseNegative'])))
        #ca_R = float(metricsDict['ca']['truePositive'])/(float(metricsDict['ca']['truePositive'])+float(float(metricsDict['ca']['falseNegative'])))
        #gl_R = float(metricsDict['gl']['truePositive'])/(float(metricsDict['gl']['truePositive'])+float(float(metricsDict['gl']['falseNegative'])))
        #es_R = float(metricsDict['es']['truePositive'])/(float(metricsDict['es']['truePositive'])+float(float(metricsDict['es']['falseNegative'])))
        #en_R = float(metricsDict['en']['truePositive'])/(float(metricsDict['en']['truePositive'])+float(float(metricsDict['en']['falseNegative'])))
        #pt_R = float(metricsDict['pt']['truePositive'])/(float(metricsDict['pt']['truePositive'])+float(float(metricsDict['pt']['falseNegative'])))

        #Metrics for F1-measure
        #eu_F = ca_F = gl_F = es_F = en_F = pt_F = 0.00

        fMeasure = 1.00

        if eu_P == 0 or eu_R == 0:
            eu_F = 0.0
        else:
            eu_F = (((fMeasure**2) + 1)*eu_P*eu_R)/((fMeasure**2)*eu_P+eu_R)

        if ca_P == 0 or ca_R == 0:
            ca_F = 0.0
        else:
            ca_F = (((fMeasure**2)+1)*ca_P*ca_R)/((fMeasure**2)*ca_P+ca_R)

        if gl_P == 0 or gl_R == 0:
            gl_F = 0.0
        else:
            gl_F = (((fMeasure**2)+1)*gl_P*gl_R)/((fMeasure**2)*gl_P+gl_R)

        if es_P == 0 or es_R == 0:
            es_F = 0.0
        else:
            es_F = (((fMeasure**2)+1)*es_P*es_R)/((fMeasure**2)*es_P+es_R)

        if en_P == 0 or en_R == 0:
            en_F = 0.0
        else:
            en_F = (((fMeasure**2)+1)*en_P*en_R)/((fMeasure**2)*en_P+en_R)

        if pt_P == 0 or pt_R == 0:
            pt_F = 0.0
        else:
            pt_F = (((fMeasure**2)+1)*pt_P*pt_R)/((fMeasure**2)*pt_P+pt_R)

        #eu_F = ((fMeasure**2)*eu_P*eu_R)/(eu_P+eu_R)
        #ca_F = ((fMeasure**2)*ca_P*ca_R)/(ca_P+ca_R)
        #gl_F = ((fMeasure**2)*gl_P*gl_R)/(gl_P+gl_R)
        #es_F = ((fMeasure**2)*es_P*es_R)/(es_P+es_R)
        #en_F = ((fMeasure**2)*en_P*en_R)/(en_P+en_R)
        #pt_F = ((fMeasure**2)*pt_P*pt_R)/(pt_P+pt_R)

        #accuracy , macro-F1 & weighted-average-F1
        #accuracy, macroF1, weightedAvgF1 = 0.00

        #Calculate accuracy
        accuracy = float(countCorrect)/(float(countCorrect)+float(countWrong))

        #Calculate macro F1 measure
        macroF1 = (eu_F + ca_F + gl_F + es_F + en_F + pt_F) / 6.00

        #Calculate total count
        totalCount = float(metricsDict['eu']['modelCount']) + float(metricsDict['ca']['modelCount']) + float(metricsDict['gl']['modelCount']) + float(metricsDict['es']['modelCount']) + float(metricsDict['en']['modelCount']) + float(metricsDict['pt']['modelCount'])
        
        #Calculate weighted Average F1
        weightedAvgF1 = ((float(metricsDict['eu']['modelCount'])*eu_F) + (float(metricsDict['ca']['modelCount'])*ca_F) + (float(metricsDict['gl']['modelCount'])*gl_F) + (float(metricsDict['es']['modelCount'])*es_F) + (float(metricsDict['en']['modelCount'])*en_F) + (float(metricsDict['pt']['modelCount'])*pt_F))/totalCount


        #Compose file name
        evalFileName = "eval_" + str(len(self.vocabulary)) +"_"+ str(self.ngram) +"_"+ str(self.smoothing) +".txt"
        
        #Hard code file name for Build Your Own Model
        if byomFlag == 1:
            evalFileName = "eval_myModel.txt"

        file = open(evalFileName, 'w')


        evalAccuracyOutputString = str(accuracy) + "\n"
        file.write(evalAccuracyOutputString)
        
        evalPrecisionOutputString = str(eu_P) + "  " + str(ca_P) + "  " + str(gl_P) + "  " + str(es_P) + "  " + str(en_P) + "  " + str(pt_P) + "\n"
        file.write(evalPrecisionOutputString)

        evalRecallOutputString = str(eu_R) + "  " + str(ca_R) + "  " + str(gl_R) + "  " + str(es_R) + "  " + str(en_R) + "  " + str(pt_R) + "\n"
        file.write(evalRecallOutputString)

        evalF1MeasureOutputString = str(eu_F) + "  " + str(ca_F) + "  " + str(gl_F) + "  " + str(es_F) + "  " + str(en_F) + "  " + str(pt_F) + "\n"
        file.write(evalF1MeasureOutputString)

        evalOverallOutputString = str(macroF1) + "  " + str(weightedAvgF1) + "\n"
        file.write(evalOverallOutputString)

        #Finally
        file.close()
class LangModel_GroupAwesome(LangModel):
    #parameterized constructor
    def __init__(self,vocabulary=-1,ngram=-1,trainingFile="",testingFile="" , filterPatterns=[], specialCharacterSequencesByLanguage={}):
            LangModel.__init__(self , vocabulary , ngram ,0.0, traitrainingFile , TestestingFile)
            self.filterPatterns= filterPatterns
            self.specialCharacterSequencesByLanguage =specialCharacterSequencesByLanguage
    
    def filterTrainingSet(self):
        pass

    def evaluateGivenFeatures(self):
        pass

    def evaluateAppropriateSmoothValue(self):
        switcherLanguage = {
             0: self.EU,
             1: self.CA,
             2: self.GL,
             3: self.ES,
             4: self.EN,
             5: self.PT
            }
       
        for i in range (6):
            table = switcherLanguage.get(i)
            table.evaluateSmoothVal()

# Main

test = LangModel(1, 2, 0.1)
test.generateProbabilityTable()
#print(test.languageProbability)
test.printResults()
