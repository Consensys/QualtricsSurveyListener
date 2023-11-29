# Python 3

import requests
import zipfile
import json
import io, os
import sys
import re
import csv
import time
import asyncio
import aiofiles
import aiohttp
from aiohttp import ClientSession
from utils import strip_tags, is_float, is_int, Diff, getKeyList, makeAgeBin

#import env file library
from dotenv import load_dotenv
load_dotenv()

#Functions

# Function that starts asynchronous calls to POST survey data
async def sendNewResponses(newResponseData):
    # announce start of function for console
    print("SENDING NEW RESPONSE TO API...\n")

    # define POST_REGISTER_RESPONSE_URL
    url = os.getenv("POST_REGISTER_RESPONSE_URL")

    # changed test
    # start asynchronous POST Calls
    async with aiohttp.ClientSession() as session:
        # post_tasks = []
        # prepare the coroutines that poat
        for response in newResponseData:
            # asynchronous call method
            # post_tasks.append(postResponse(session, url, response))

            # synchronous call method
            callResponse = await postResponse(url, response)
            print("I'm back! \n")
            print(callResponse)

        # asynchronous --> now execute them all at once
        '''
        try:
            await asyncio.gather(*post_tasks)
        except:
            print("POST Request was not successful.\n")
            await sendNewResponses(newResponseData)
        '''
    # changed test

    # Step 3: return true when complete
    return True

# Function that does work for each call being made
# asynchronous method --> async def postResponse(session, url, response):
async def postResponse(url, response):
    # Step 1: Create parameters needed for API CALL
    token = os.getenv("TOKEN")

    #define more complex values before setting dict
    responseAnswers = json.dumps(response['answers'], separators=(',', ':'))

    #set payload
    bodyPayload = {
        "responseId": response['responseId'],
        "startDate": response['startDate'],
        "endDate": response['endDate'],
        "recordedDate": response['recordedDate'],
        "location": {
            "longitude": response['locationLongitude'],
            "latitude": response['locationLatitude']
        },
        "userLanguage": response['userLanguage'],
        "response": response['originalResponseString'],
        "surveyId": response['surveyId'],
        "workerAge": response['workerAge'],
        "workerFactory": response['workerFactory'],
        "workerGender": response['workerGender'],
        "surveyNumber": response['surveyNumber'],
        "responseAnswers": response['answers'],
        "methodName": "RegisterSurvey",
        "blockchain": "kaleido"
    }

    headers = {
        "content-type": "application/json",
        "Authorization": 'Bearer {}'.format(token)
    }

    '''
    # asynchronous call method
    async with session.post(url, data=json.dumps(bodyPayload, separators=(',', ':')), headers=headers) as answer:
      data = await answer.text()
      print("-> Posted response  to api \n")
      print (data)
    '''
    # synchronous call method
    print("MAKING THE ACTUAL CALL..\n")
    blockRequest = requests.request("POST", url, headers=headers, data=json.dumps(bodyPayload, separators=(',', ':')), stream=True)
    return blockRequest.json()

# Function that checks which responses are already in DB (by responseId)
def checkIfExistingRecord(responseData):
    print("CHECKING IF RECORDS EXIST ALREADY....\n")

    # Step 1: Make a call to get all existing records and store in array
    requestCheckUrl = os.getenv("GET_REPORTS_IDS_URL")
    # token = os.getenv("TOKEN")
    headers = {
        "content-type": "application/json",
    }

    print("MAKING CURRENT RESPONSE CALL: \n")
    requestArchivedResponses = requests.request("GET", requestCheckUrl, headers=headers, stream=True)
    requestArchivedResponses = requestArchivedResponses.json()

    print("REQUEST RESPONSE: \n")
    print(requestArchivedResponses)

    # Step 2: Get list of requestIds from each list
    newRequests = getKeyList(responseData, "responseId")
    oldRequests = requestArchivedResponses['responseIds']

    print("NEW REQUESTS - " +  str(len(newRequests)) + ": \n")
    print("OLD REQUESTS - " +  str(len(oldRequests)) + ": \n")

    # Step 3: Check to see if records are not in that existing list
    uniqueList = [x for x in newRequests if x not in oldRequests]
    print("UNIQUE REQUESTS - " +  str(len(uniqueList)) + ": \n")
    newResponseData = []
    for listItem in uniqueList:
        for response in responseData:
            if response['responseId'] == listItem:
                newResponseData.append(response)

    # Step 4: Return list of new-to-add records
    print("LIST HAS BEEN PROCESSED. LENGTH IS : " + str(len(newResponseData)) + "\n")
    return newResponseData

# Function mapping responses to questions for cleaner json
def mapQuestionsToResponses(responseData, questionData, surveyId):
    print("STARTING QUESTION TO RESPONSE MAPPING PROCESS...\n")

    # Step 1: Create new array for all cleansed answers
    cleanResponses = []

    # Step 2: Consolidate muti-tier question format in response data
    for response in responseData:
        if float(response['values']['progress']) == 100:
            try:
                cleanResponse = dict()
                cleanResponse['responseId'] = response['responseId']
                cleanResponse['startDate'] = response['values']['startDate']
                cleanResponse['endDate'] = response['values']['endDate']
                cleanResponse['recordedDate'] = response['values']['recordedDate']
                cleanResponse['locationLongitude'] = response['values']['locationLongitude']
                cleanResponse['locationLatitude'] = response['values']['locationLatitude']
                cleanResponse['userLanguage'] = response['values']['userLanguage']
                cleanResponse['originalResponseString'] = str(response)
                cleanResponse['surveyId'] = surveyId
            except:
                print("Error: An exception occurred: One of the response keys is missing or mispelled in the base code. The response is the following: \n")
                print(response)
        else:
            continue

        # we need to read all question attributes in labels
        # segregate answers by question title
        # specifically get surveyNumber, Submitter Gender, Submitter Age
        responseLabelData = response['labels']
        answers = []
        for key, value in responseLabelData.items() :
            # only focus on the keys that are QID answers
            if "QID" in key:
                # assign varying indices needed
                qid = key
                questionNumber = qid.split("ID")[1]
                subQuestionNumber = "none"

                print("PROCESSING ANSWER: " + qid + "\n")
                print("QUESTION NUMBER NOW: " + questionNumber + "\n")
                print("SUB QUESTION NUMBER NOW: " + subQuestionNumber + "\n")

                # account for varying question types
                if "_" in qid:
                    subQuestionNumber = questionNumber.split("_")[1]
                    questionNumber = questionNumber.split("_")[0]
                baseQuestionID = "QID" + questionNumber

                if "#" in qid:
                    # fix baseQuestionID to proper string
                    baseQuestionID = qid.split("#")[0]

                # communicate current values
                print("QUESTION NUMBER NOW: " + questionNumber + "\n")
                print("SUB QUESTION NUMBER NOW: " + subQuestionNumber + "\n")
                print("BASE QUESTION ID: " + baseQuestionID + "\n")

                # create question type index dict
                questionTypes = {
                    "MC": "Multiple Choice",
                    "TE": "Text Entry",
                    "DB": "Descriptive Text or Graphics",
                    "RO": "Ranked Order",
                    "Slider": "Slider Question",
                    "SBS": "Side by Side",
                    "Matrix": "Matrix Table"
                }

                if questionData[baseQuestionID]['QuestionType'] in ["MC", "TC", "TE", "DB"]:
                    # dynamically create new answer dict
                    answer = responseLabelData[qid]
                    if "NPS_GROUP" in qid:
                        if responseLabelData[qid] == "Promoter":
                            answer = "9 or 10"
                        elif responseLabelData[qid] == "Passive":
                            answer = "7 or 8"
                        else:
                            answer = "0-6"
                    answers.append({
                        'QuestionText': questionData[baseQuestionID]['QuestionText'],
                        "QuestionType": questionTypes[questionData[baseQuestionID]['QuestionType']],
                        "QuestionAnswer": answer,
                        "QuestionId": qid
                    })
                elif questionData[baseQuestionID]['QuestionType'] in ["RO", "Slider", "Matrix"]:
                    # dynamically create new answer dict
                    matrixQuestions = questionData[baseQuestionID]['QuestionChoices']
                    if is_int(subQuestionNumber):
                        # find which of the questions is being answered
                        answers.append({
                            'QuestionText': questionData[baseQuestionID]['QuestionText'] + " ("  + strip_tags(matrixQuestions[subQuestionNumber]['Display']) + ")",
                            "QuestionType": questionTypes[questionData[baseQuestionID]['QuestionType']],
                            "QuestionAnswer": responseLabelData[qid],
                            "QuestionId": qid
                        })
                elif questionData[baseQuestionID]['QuestionType'] == "SBS":
                    # dynamically create new answer dict
                    # EX: subQuestionNumber = 1
                    # EX: questionNumber = 8#1
                    # EX: baseQuestionID = QID8#1

                    # create new variable side to determine question section
                    questionSection = questionNumber.split("#")[1]

                    # collect statements used across question sections
                    matrixQuestions = questionData[baseQuestionID]['QuestionChoices']

                    answers.append({
                        'QuestionText': questionData[baseQuestionID]['QuestionText'] + " ("  + strip_tags(matrixQuestions[subQuestionNumber]['Display']) + ": Question Section " + questionSection + ")",
                        "QuestionType": "Side by Side",
                        "QuestionAnswer": responseLabelData[qid],
                        "QuestionId": qid
                    })

        # set answer to cleanResponse
        cleanResponse['answers'] = answers

        # set respondent age, gender, and survey number
        surveyNumber = ""
        for answer in cleanResponse['answers']:
            if "how old are you" in answer["QuestionText"].lower():
                try:
                    age = int(answer["QuestionAnswer"])
                    cleanResponse['workerAge'] = makeAgeBin(age)
                except ValueError:
                    cleanResponse['workerAge'] = answer["QuestionAnswer"]
            if "what is your gender" in answer["QuestionText"].lower():
                cleanResponse['workerGender'] = answer["QuestionAnswer"]
            if "survey number" in answer["QuestionText"].lower():
                surveyNumber += str(answer["QuestionAnswer"])
                print(surveyNumber)
            if "which factory do you work at" in answer["QuestionText"].lower():
                cleanResponse['workerFactory'] = answer["QuestionAnswer"]

        cleanResponse['surveyNumber'] = str(surveyNumber)

        # final cleanse of cleanResponse then append clean response
        attributes = ('surveyNumber', 'workerFactory', 'workerAge', 'answers', 'responseId', 'startDate', 'endDate', 'recordedDate','locationLongitude', 'locationLatitude', 'userLanguage' ,'originalResponseString', 'surveyId', 'workerGender')

        if all(key in cleanResponse for key in attributes):
            print("CHECKING IF TEST RESPONSE..\n")
            # 00000, 11111; 12345; 99999; 10000
            if (cleanResponse['surveyNumber'] != "00000" or cleanResponse['surveyNumber'] != "11111" or cleanResponse['surveyNumber'] != "12345" or cleanResponse['surveyNumber'] != "99999" or cleanResponse['surveyNumber'] != "10000" or cleanResponse['surveyNumber'] != "1000" or cleanResponse['surveyNumber'] != "5408"):
                print("NOT TEST RESPONSE. ADDING TO LIST!..\n")
                cleanResponses.append(cleanResponse)

    # Step 3: return clean responses
    print("COMPLETED ANSWER TO QUESTION MATCHING!...\n")
    return cleanResponses


# Function Getting the survey questions
def getSurveyQuestions(surveyId, dataCenter, apiToken):
    print("GETTING SURVEY QUESTIONS...\n")

    # Step 1: Set API call parameters
    baseUrl = "https://{0}.qualtrics.com/API/v3/survey-definitions/{1}/questions/".format(dataCenter, surveyId)
    headers = {
    "content-type": "application/json",
    "x-api-token": apiToken,
    }

    # Step 2: Make the API CALL
    questionRequestUrl = baseUrl
    downloadRequestResponse = requests.request("GET", questionRequestUrl, headers=headers, stream=True)
    surveyQuestionData = json.loads(downloadRequestResponse.content)['result']['elements']

    # Step 3: Run through json object to get needed information
    # set questionData dict
    questionData = dict()
    # set counter
    counter = 0
    # set question type tracker
    questionTypes = []
    for question in surveyQuestionData:
        # increment counter
        counter += 1

        # conditionally set choices dict
        choices = "none"
        if "Choices" in question:
            choices = question['Choices']

        # set new question data dict
        questionData[question['QuestionID']] = {
            "ListPosition": counter,
            "QuestionText": strip_tags(question['QuestionText']),
            "QuestionDescription": strip_tags(question['QuestionDescription']),
            "QuestionType": strip_tags(question['QuestionType']),
            "QuestionChoices": choices
        }

        # check to see if question type has been captured before
        if question['QuestionType'] not in questionTypes:
            questionTypes.append(question['QuestionType'])

    # overview of question analysis and processing
    print("THERE ARE " + str(len(questionData)) + " QUESTIONS LOADED..\n")
    print("THERE ARE " + str(len(questionTypes)) + " QUESTION TYPES: \n")

    return questionData


# Function reading in the survey response data
async def readResponseFile(filename, surveyId, dataCenter, apiToken):
    print("READ RESPONSE PROCESS STARTED...\n")
    # Step 1: Read JSON data into the datastore variable
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)

    # Step 2: Access datastore to ensure it is working fine
    print("READ TEST CONDUCTING...\n")
    print("FIRST RESPONSE ID IS: " + str(datastore["responses"][0]["responseId"]))
    responseData = datastore["responses"]

    # Step 3: Match questions attribute titles to survey questions
    questionData = getSurveyQuestions(surveyId, dataCenter, apiToken)

    # Step 4: Map question data to response data
    cleanResponses = mapQuestionsToResponses(responseData, questionData, surveyId)

    # Step 5: Send clean data to compare against existing data
    newResponseData = checkIfExistingRecord(cleanResponses)

    # Step 6: Send new data for API Call
    truth = await sendNewResponses(newResponseData)

    # Step 7: Start process over agin (every 5 minutes)
    rest = 300
    if truth:
        print("PROCESS COMPLETED! RESTING " + str(rest) + " SECONDS FOR NEXT ITERATION...\n")
        time.sleep(rest)
        main()

# Function exporting survey file
async def exportSurvey(apiToken,surveyId, dataCenter, fileFormat):
    print("EXPORT SURVEY PROCESS STARTED...\n")

    # Setting static parameters
    requestCheckProgress = 0.0
    progressStatus = "inProgress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
    }

    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '"}'
    downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
    progressId = downloadRequestResponse.json()["result"]["progressId"]
    print(downloadRequestResponse.text)

    # Step 2: Checking on Data Export Progress and waiting until export is ready
    while progressStatus != "complete" and progressStatus != "failed":
        print ("progressStatus=", progressStatus)
        requestCheckUrl = baseUrl + progressId
        requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
        requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
        print("Download is " + str(requestCheckProgress) + " complete")
        progressStatus = requestCheckResponse.json()["result"]["status"]

    #step 2.1: Check for error
    if progressStatus is "failed":
        raise Exception("export failed")

    fileId = requestCheckResponse.json()["result"]["fileId"]

    # Step 3: Downloading file
    requestDownloadUrl = baseUrl + fileId + '/file'
    requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)

    # Step 4: Unzipping the file
    zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("QualtricsDownload")
    print('Survey Response Download Complete\n')

    # Step 5: Read in the json the file
    folderContents = os.listdir('QualtricsDownload')
    await readResponseFile("QualtricsDownload/" + folderContents[0], surveyId, dataCenter, apiToken)

async def main():
    #start message for script
    print("STARTING SCRIPT....\n")
    #basic constant variables
    fileFormat = "json"

    print("ENSURING ENV. VARIABLES ARE SUBMITTED....\n")
    try:
      QUALTRICS_DATA_CENTER = os.getenv("QUALTRICS_DATA_CENTER")
      QUALTRICS_SURVEY_ID = os.getenv("2017_REAL_SURVEY_ID")
      QUALTRICS_API_TOKEN = os.getenv("QUALTRICS_API_TOKEN")
      QUALTRICS_USER_ID = os.getenv("QUALTRICS_USER_ID")
      AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
      AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    except KeyError:
      print("make sure to set all environment variables\n")
      sys.exit(2)

    print("LISTENING TO THE FOLLOWING SURVEY ON QUALTRICS: " + str(QUALTRICS_SURVEY_ID) + "\n")
    r = re.compile('^SV_.*')
    m = r.match(QUALTRICS_SURVEY_ID)
    if not m:
       print ("survey Id must match ^SV_.*")
       sys.exit(2)

    print("STARTING EXPORT OF INCOMING SURVEY RESULTS...\n")
    await exportSurvey(QUALTRICS_API_TOKEN, QUALTRICS_SURVEY_ID, QUALTRICS_DATA_CENTER, fileFormat)

if __name__== "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
