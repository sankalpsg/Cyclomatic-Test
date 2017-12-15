# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 22:51:12 2017

@author: Sankalp
"""

import json, requests, time, getpass
from flask import Flask
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)


class getRepo(Resource): # API for Slaves to get Repo Info
    def __init__(self):  
        global master  
        self.server = master  
        super(getRepo, self).__init__()  
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument('status', type=int, location = 'json')  
        self.reqparser.add_argument('complexity', type=float, location='json')

    def get(self):
        args = self.reqparser.parse_args()
        if args['status'] == False:  
            return {'repo': "https://github.com/TheAlgorithms/Python"}
        if args['status'] == True:  # Successful import of Repository
            self.server.slavesConnected += 1
            if self.server.slavesConnected == self.server.numberOfSlaves:  # All slaves connected
                self.server.startTime = time.time()  # Start  timer
            print("SLAVE NUMBER: {}".format(self.server.slavesConnected))

api.add_resource(getRepo, "/repo", endpoint="repo")


#  Cyclomatic Complexity Values API
class complexityAPI(Resource):
    def __init__(self):  
        global master 
        self.server = master  
        super(complexityAPI, self).__init__()  
        self.reqparser = reqparse.RequestParser()

        self.reqparser.add_argument('commitSha', type=str, location = 'json') 
        self.reqparser.add_argument('complexity', type=float, location='json')

    def get(self):
        if self.server.slavesConnected < self.server.numberOfSlaves: #Waiting for Slaves to Connect
            time.sleep(0.1)
            return {'sha': -2}
        if len(self.server.commitList) == 0:  # All Commits Covered
            return {'sha': -1}
        commitCount = self.server.commitList[0] 
        del self.server.commitList[0] 
        print("Sent: {}".format(commitCount))
        return {'sha':commitCount}


    def post(self):
        args = self.reqparser.parse_args()  # parse the arguments from the POST
        print("Received sha {}".format(args['commitSha']))
        print("Received complexity {}".format(args['complexity']))
        # Form list of cyclomatic complexities
        self.server.cycloList.append({'sha':args['commitSha'], 'complexity':args['complexity']})
        print(self.server.cycloList)
        print(self.server.commitList)
        if len(self.server.cycloList) == self.server.totalCountOfCommits:  # All commits have been processed
            finishTime = time.time() - self.server.startTime
            print("finished in {} seconds".format(finishTime))
            print(len(self.server.cycloList))
            totalAverageCC = 0
            for i in self.server.cycloList:
                if i['complexity'] > 0:
                    totalAverageCC += i['complexity']
                else:
                    print("Commit {} has no computable files".format(i['sha']))
            totalAverageCC = totalAverageCC / len(self.server.cycloList)
            print("OVERALL CYCLOMATIC COMPLEXITY FOR REPOSITORY: {}".format(totalAverageCC))
        return {'success':True}


api.add_resource(complexityAPI, "/cyclomatic", endpoint="cyclomatic")


class delegator():
    def __init__(self):
        
        self.numberOfSlaves = input("Count of slave nodes")
        self.numberOfSlaves = int(self.numberOfSlaves)
        self.slavesConnected = 0  # Slaves Connected to Manager
        self.startTime = 0.0  
       
        #Mention your git UserName and Password
        username = input("Mention your Username ")
        password = getpass.getpass("Mention your Password")
        morePages = True  # to check multiple pages on GIT API
        repo_Page = 1  # Current page of github API repo info
        self.commitList = []  # List containing all commit sha values
        while morePages:
            req = requests.get("https://api.github.com/repos/TheAlgorithms/Python/commits?page={}&per_page=100"
                                 .format(repo_Page), auth=(username, password))  # Authenticated API request
            json_str = json.loads(req.text)
            if len(json_str) < 2:
                morePages = False
            else:
                for x in json_str:
                    self.commitList.append(x['sha'])
                    print("Commit Sha: {}".format(x['sha']))
                print("\n")
                repo_Page += 1
        self.totalCountOfCommits = len(self.commitList)  # Count of commits in Repository
        self.cycloList = []
        print("Count of commits: {}".format(self.totalCountOfCommits))


if __name__ == "__main__":
    master = delegator()
    app.run(port=8081)  #Port 8081