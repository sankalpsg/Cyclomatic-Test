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
        self.listOfCCs = []
        print("Count of commits: {}".format(self.totalCountOfCommits))


if __name__ == "__main__":
    master = delegator()
    app.run(port=8081)  #Port 8081